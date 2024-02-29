from casadi import *
import matplotlib.pyplot as plt
import utils
from activity_reader import ActivityReader
from scipy.ndimage import gaussian_filter1d

def create_multistage_optimization(distance, elevation, num_steps, final_time_guess, smooth_power_constraint = False):
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

    sigma = 10
    smoothed_elev = gaussian_filter1d(elevation, sigma)

    slope = utils.calculate_gradient(distance, smoothed_elev)

    interpolated_slope = interpolant('Slope', 'bspline', [distance], slope)

    f = lambda x,u: vertcat(x[1], 
                        (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                        -(u-cp))

    # With w'bal ODE as physiological model 
    # f = lambda x,u,s: vertcat(x[1], 
    #                        (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*s*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
    #                        -(u-cp)*(1-utils.sigmoid(u, cp, 3)) + (1-w_bal/w_prime)*(cp-u)*utils.sigmoid(u, cp, 3)) 

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
    opti.subject_to(opti.bounded(0, U, 500)) 
    opti.subject_to(opti.bounded(0, w_bal, w_prime))
    opti.subject_to(opti.bounded(1, speed, 25))

    # Set boundary conditions
    opti.subject_to(pos[0]==0) 
    opti.subject_to(speed[0]==1) 
    opti.subject_to(pos[-1]==distance[-1])
    opti.subject_to(w_bal[0]==w_prime)

    opti.subject_to(T>=0) 
    #opti.subject_to(speed > 1)

    # Provide an initial guess for the solver
    opti.set_initial(T, final_time_guess)
    opti.set_initial(speed, 10)
    opti.set_initial(U, cp)

    p_opts = {"expand": False}
    s_opts = {"max_iter": 300000}
    opti.solver('ipopt') 
    return opti, T, U, X


def solve_multistage_optimization(distance, elevation, final_time_guess, num_steps, smooth_power_constraint):
    opti, T, U, X = create_multistage_optimization(distance, elevation, num_steps, final_time_guess, smooth_power_constraint)
    sol = opti.solve() 
    return sol, T, U, X
        

activity = ActivityReader("Mech_isle_loop_time_trial.tcx")
#activity = ActivityReader("Canopies_and_coastlines_time_trial.tcx")
#activity = ActivityReader("Hilly_route.tcx")
activity.remove_unactive_period(400)

time_initial_guess = activity.distance[-1]/1000 * 120
N = round(activity.distance[-1]/20)
sol, T, U, X = solve_multistage_optimization(activity.distance, activity.elevation, time_initial_guess, N, False)
cp = 265
w_prime = 26630

optimal_power = sol.value(U)
optimal_time = sol.value(T)
pos = sol.value(X[0,:])
velocity = sol.value(X[1,:])
w_bal = sol.value(X[2,:])
t_grid = linspace(0, optimal_time, N+1)

fig, ax = plt.subplots(3,1)

ax[0].set_title(f"The optimal time is {round(optimal_time/60, 2)} min")
ax[0].set_ylabel("Power [W]")
ax[0].set_ylim(0,550)
ax[0].plot(pos, optimal_power)
ax[0].plot(round(pos[-1])*[cp], color='tab:gray', linestyle='dashed')
ax[0].legend(["Optimal power output", "CP"])
ax1_twin = ax[0].twinx()
ax1_twin.set_ylabel('Elevation [m]', color='tab:red')
ax1_twin.plot(activity.distance, activity.elevation, color='tab:red')
ax1_twin.tick_params(axis='y', labelcolor='tab:red')
ax1_twin.legend(["Elevation Profile"])

ax[1].set_ylabel("Velocity [m/s]")
ax[1].set_ylim(0,20)
ax[1].plot(pos, velocity)
ax[1].legend(["Velocity"])
ax2_twin = ax[1].twinx()
ax2_twin.set_ylabel('Elevation [m]', color='tab:red')
ax2_twin.plot(activity.distance, activity.elevation, color='tab:red')
ax2_twin.tick_params(axis='y', labelcolor='tab:red')
ax2_twin.legend(["Elevation Profile"])

ax[2].set_ylabel("W'balance [J]")
ax[2].set_xlabel("Position [m]")
ax[2].set_ylim(0, 27000)
ax[2].plot(pos, w_bal)
ax[2].legend(["W'balance"])
ax3_twin = ax[2].twinx()
ax3_twin.set_ylabel('Elevation [m]', color='tab:red')
ax3_twin.plot(activity.distance, activity.elevation, color='tab:red')
ax3_twin.tick_params(axis='y', labelcolor='tab:red')
ax3_twin.legend(["Elevation Profile"])
plt.show()


smoothed_power = gaussian_filter1d(activity.power, 4)
fig2, ax4 = plt.subplots(1,1)
ax4.plot(pos, optimal_power)
ax4.plot(activity.distance, smoothed_power)
ax4.plot(round(pos[-1])*[cp], color='tab:gray', linestyle='dashed')
ax4.legend([f"Optimal power (avg: {round(np.mean(optimal_power))}W)", f"Smoothed actual power (avg: {round(np.mean(smoothed_power))}W)", "CP"])
ax4.set_xlabel("Position [m]")
ax4.set_ylabel("Power [W]")
ax4_twin = ax4.twinx()
ax4_twin.set_ylabel('Elevation [m]', color='tab:red')
ax4_twin.plot(activity.distance, activity.elevation, color='tab:red')
ax4_twin.tick_params(axis='y', labelcolor='tab:red')
ax4_twin.legend(["Elevation Profile"])
plt.show()


w_bal_opt = utils.w_prime_balance_ode(optimal_power, t_grid, cp, w_prime)
w_bal_real = utils.w_prime_balance_ode(smoothed_power, activity.time, cp, w_prime)
w_bal_opt = [float(elem) for elem in w_bal_opt]

plt.plot(t_grid, w_bal_opt, 'o-')
plt.plot(activity.time, w_bal_real)
plt.legend(["W'balance optimal", "W'balance actual"])
plt.ylabel("W'balance [J]")
plt.xlabel("Distance [m]")
plt.show()

difference = [t_grid[i+1]-t_grid[i] for i in range(1,100)]
print(difference)