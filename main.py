import optimization.optimal_pacing as opt
import utils.utils as utils
import activity_reader_tcx.activity_reader as act
from plotting import optimization_plots
import matplotlib.pyplot as plt
import casadi as ca

# activity = act.ActivityReader("Mech_isle_loop_time_trial.tcx")
# activity.remove_period_after(4000)
                                
# activity = act.ActivityReader("Greater_london_flat_race.tcx")
# activity.remove_period_after(17500)

# activity = act.ActivityReader("Canopies_and_coastlines_time_trial.tcx")
# activity.remove_period_after(27800)

# activity = act.ActivityReader("Richmond_UCI_worlds.tcx")
# activity.remove_period_after(16200)
                                
# activity = act.ActivityReader("Hilly_route.tcx")
# activity.remove_period_after(9600)

activity = act.ActivityReader("Downtown_titans.tcx")
activity.remove_period_after(24600)

distance_simplified, elevation_simplified = utils.simplify_track(activity.distance, activity.elevation)

time_initial_guess = round(activity.distance[-1]/1000*120)
N = round(activity.distance[-1]/5)
cp = 265
w_prime = 26630

init_sol, opti, T, U, X = opt.solve_opt(distance_simplified, elevation_simplified, N, time_initial_guess, cp, solver='ipopt', 
                                        smooth_power_constraint=True, w_bal_ode=True, euler_method=True)
optimization_plots.plot_optimization_results(init_sol, U, X, T, distance_simplified, elevation_simplified)
print(len(init_sol.value(U)))

sol, opti, T, U, X = opt.solve_opt_warmstart(activity.distance, activity.elevation, N, 
                                             init_sol.value(T), init_sol.value(U), init_sol.value(X[0,:]), 
                                             init_sol.value(X[1,:]), init_sol.value(X[2,:]), solver='ipopt', 
                                             smooth_power_constraint=True, w_bal_ode=True, euler_method=True)
optimization_plots.plot_optimization_results(sol, U, X, T, activity.distance, activity.elevation)
print(len(sol.value(U)))

t_grid = ca.linspace(0, sol.value(T), N+1)

w_bal_actual = utils.w_prime_balance_ode(sol.value(U),t_grid, cp, w_prime)
w_bal_casadi = sol.value(X[2,:])
w_bal_actual = [float(elem) for elem in w_bal_actual]

print(w_bal_actual[-1]-w_bal_casadi[-1])

fig, ax = plt.subplots()

ax.plot(sol.value(X[0,:]), w_bal_actual)
ax.plot(sol.value(X[0,:]), w_bal_casadi)
ax.legend(["Actual w_bal", "Casadi w_bal"])

ax2 = ax.twinx()
ax2.plot(activity.distance, activity.elevation, color='tab:red')
ax2.set_ylabel('Elevation [m]', color='tab:red')
ax.set_ylabel("W'balance [J]")
ax.set_xlabel("Distance [m]")
plt.show()

plt.plot(t_grid, w_bal_actual)
plt.plot(t_grid, w_bal_casadi)
plt.legend(["Actual W'bal", "Casadi W'bal"])
plt.ylabel("W'balance [J]")
plt.xlabel("Time [s]") 
plt.show()