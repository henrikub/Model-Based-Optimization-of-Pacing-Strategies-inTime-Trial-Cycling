from casadi import *
import matplotlib.pyplot as plt
import utils

def create_multistage_optimization(gradients, stage_distances, num_steps, final_time_guess, smooth_power_constraint = False):
    N = num_steps
    opti = Opti()
    X = opti.variable(3, N+1)
    pos = X[0,:]
    speed = X[1,:]
    w_bal = X[2,:]
    U = opti.variable(1,N+1)
    T = opti.variable()

    mass_rider = 78
    mass_bike = 8
    m = mass_bike + mass_rider
    g = 9.81
    my = 0.004
    b0 = 0.091
    b1 = 0.0087
    Iw = 0.14
    r = 0.33
    Cd = 0.7
    rho = 1.2
    A = 0.4
    eta = 1
    w_prime = 26630
    cp = 265
    
    slope = utils.get_slope_arr(gradients, stage_distances)
    pos_grid = np.linspace(0, len(slope), len(slope))

    interpolated_slope = interpolant('Slope', 'bspline', [pos_grid], slope)

    f = lambda x,u: vertcat(x[1], 
                        (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                        -(u-cp))

    # With w'bal ODE as physiological model 
    # f = lambda x,u,s: vertcat(x[1], 
    #                        (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*s*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
    #                        -(u-cp)*(1-utils.sigmoid(u, cp, 3)) + (1-w_bal/w_prime)*(cp-u)*utils.sigmoid(u, cp, 3)) 


    total_distance = sum(stage_distances)
    steps_per_stage = [int(stage/total_distance*N) for stage in stage_distances]
    start = 0

    s = np.zeros(num_steps)
    for grade, steps in zip(gradients, steps_per_stage):
        s[start:start+steps] = grade
        start += steps

    dt = T/N 
    for k in range(N): 
        k1 = f(X[:,k], U[:,k])
        k2 = f(X[:,k] + dt/2*k1, U[:,k])
        k3 = f(X[:,k] + dt/2*k2, U[:,k])
        k4 = f(X[:,k] + dt*k3, U[:,k])
        x_next = X[:,k] + dt/6*(k1+2*k2+2*k3+k4)
        opti.subject_to(X[:,k+1] == x_next)

    
    if smooth_power_constraint:
        opti.minimize(T + 0.000005 * sumsqr(U[:,1:] - U[:,:-1])) 
    else:
        opti.minimize(T) 

    # Set the path constraints
    opti.subject_to(opti.bounded(0,U,500)) # control is limited
    opti.subject_to(opti.bounded(0,w_bal,w_prime))

    # Set boundary conditions
    opti.subject_to(pos[0]==0) # start at position 0
    opti.subject_to(speed[0]==1) 
    opti.subject_to(pos[-1]==total_distance)
    opti.subject_to(w_bal[0]==w_prime)

    opti.subject_to(T>=0) # time must be positive
    opti.subject_to(speed > 1)

    # Provide an initial guess for the solver
    opti.set_initial(T, final_time_guess)
    opti.set_initial(speed, 10)
    opti.set_initial(U, cp)

    opti.solver('ipopt') # set numerical backend
    return opti, T, U, X


def solve_multistage_optimization(gradients, stage_distances, max_attempts, final_time_guess, smooth_power_constraint):
    attempt = 0
    sol = 0
    done = False

    while attempt < max_attempts and done == False:
        N = round(sum(stage_distances)/10) + attempt*3
        opti, T, U, X = create_multistage_optimization(gradients, stage_distances, N, final_time_guess, smooth_power_constraint)
        try:
            sol = opti.solve() # actual solve
            done = True
            print(" ************************* Done found the solution!! ***************************")
        except RuntimeError:
            done = False
        finally:
            attempt += 1
    return sol, T, U, X
        
# Bologna simplified track
# gradients = [-0.0036, 0.0685, -0.0685, 0.0035, -0.0035, 0.0685]
# distances = [5000, 3100, 3300, 5100, 5200, 3100]
# elevation = utils.calculate_elevation_profile(gradients, distances, start_elevation=300)

gradients = [0.0, 0.05]
distances = [1000, 1000]
elevation = utils.calculate_elevation_profile(gradients, distances, start_elevation=300)

# Lutcher CCW simplified track
# gradients = [0, 0.08, -0.08, 0, 0.08]
# distances = [2700, 5900, 5900, 700, 5900]
# elevation = utils.calculate_elevation_profile(gradients, distances, start_elevation=284)
time_initial_guess = sum(distances)/1000 * 120

sol, T, U, X = solve_multistage_optimization(gradients, distances, 3, time_initial_guess, True)
cp = 265

power_output = sol.value(U)
optimal_time = sol.value(T)
pos = sol.value(X[0,:])
velocity = sol.value(X[1,:])
w_bal = sol.value(X[2,:])

elevation = utils.calculate_elevation_profile(gradients, distances, start_elevation=300)

fig, ax,  = plt.subplots(3,1)

ax[0].set_title(f"The optimal time is {round(optimal_time/60, 2)} min")
ax[0].set_ylabel("Power [W]")
ax[0].set_ylim(0,550)
ax[0].plot(pos, power_output)
ax[0].plot(round(pos[-1])*[cp], color='tab:gray', linestyle='dashed')
ax[0].legend(["Optimal power output", "CP"])
ax1_twin = ax[0].twinx()
ax1_twin.set_ylabel('Elevation [m]', color='tab:red')
ax1_twin.plot(elevation, color='tab:red')
ax1_twin.tick_params(axis='y', labelcolor='tab:red')
ax1_twin.legend(["Elevation Profile"])

ax[1].set_ylabel("Velocity [m/s]")
ax[1].set_ylim(0,20)
ax[1].plot(pos, velocity)
ax[1].legend(["Velocity"])
ax2_twin = ax[1].twinx()
ax2_twin.set_ylabel('Elevation [m]', color='tab:red')
ax2_twin.plot(elevation, color='tab:red')
ax2_twin.tick_params(axis='y', labelcolor='tab:red')
ax2_twin.legend(["Elevation Profile"])

ax[2].set_ylabel("W'balance [J]")
ax[2].set_xlabel("Position [m]")
ax[2].set_ylim(0, 27000)
ax[2].plot(pos, w_bal)
ax[2].legend(["W'balance"])
ax3_twin = ax[2].twinx()
ax3_twin.set_ylabel('Elevation [m]', color='tab:red')
ax3_twin.plot(elevation, color='tab:red')
ax3_twin.tick_params(axis='y', labelcolor='tab:red')
ax3_twin.legend(["Elevation Profile"])
plt.show()