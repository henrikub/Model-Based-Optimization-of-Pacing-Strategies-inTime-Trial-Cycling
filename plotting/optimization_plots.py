import matplotlib.pyplot as plt
import datetime

def plot_optimization_results(sol, U, X, T, distance, elevation, params, opt_details):
    cp = params.get("cp")
    alpha = params.get("alpha")
    alpha_c = params.get("alpha_c")
    c_max = params.get("c_max")
    c = params.get("c")

    optimal_power = sol.value(U)
    optimal_time = sol.value(T)
    pos = sol.value(X[0,:])
    velocity = sol.value(X[1,:])
    w_bal = sol.value(X[2,:])

    # stats = sol.stats()
    # opt_time = stats['t_wall_total']

    max_power = 4*(alpha*w_bal + cp)*(c/(alpha_c*w_bal + c_max)*(1-c/(alpha_c*w_bal + c_max)))
    fig, ax = plt.subplots(3,1, figsize=(15,10))

    ax[0].set_title(f"The optimal time is {str(datetime.timedelta(seconds=round(optimal_time)))}")
    ax[0].set_ylabel("Power [W]")
    ax[0].set_ylim(0,max(max_power)+10)
    ax[0].plot(pos, max_power)
    ax[0].plot(pos, optimal_power)
    ax[0].plot(round(pos[-1])*[cp], color='tab:gray', linestyle='dashed')
    ax[0].legend(["Maximum attainable power", "Optimal power output", "CP"])
    ax1_twin = ax[0].twinx()
    ax1_twin.set_ylabel('Elevation [m]', color='tab:red')
    ax1_twin.plot(distance, elevation, color='tab:red')
    ax1_twin.tick_params(axis='y', labelcolor='tab:red')
    ax1_twin.legend(["Elevation Profile"])

    ax[1].set_ylabel("Velocity [m/s]")
    ax[1].set_ylim(0,20)
    ax[1].plot(pos, velocity)
    ax[1].legend(["Velocity"])
    ax2_twin = ax[1].twinx()
    ax2_twin.set_ylabel('Elevation [m]', color='tab:red')
    ax2_twin.plot(distance, elevation, color='tab:red')
    ax2_twin.tick_params(axis='y', labelcolor='tab:red')
    ax2_twin.legend(["Elevation Profile"])

    ax[2].set_ylabel("W'balance [J]")
    ax[2].set_xlabel("Position [m]")
    ax[2].set_ylim(0, 27500)
    ax[2].plot(pos, w_bal)
    ax[2].legend(["W'balance"])
    ax3_twin = ax[2].twinx()
    ax3_twin.set_ylabel('Elevation [m]', color='tab:red')
    ax3_twin.plot(distance, elevation, color='tab:red')
    ax3_twin.tick_params(axis='y', labelcolor='tab:red')
    ax3_twin.legend(["Elevation Profile"])

    fig.text(0.5, 0.02, f"Integration method: {opt_details.get('integration_method')}, points = {len(distance)}, N = {opt_details.get('N')}, W'balance model: {opt_details.get('w_bal_model')}, iterations: {opt_details.get('iterations')}, time: {str(datetime.timedelta(seconds=round(opt_details.get('opt_time'))))}", horizontalalignment="center")

    plt.show()

def plot_optimization_results2(sol, U, X, T, distance, elevation, params, opt_details):
    cp = params.get("cp")
    alpha = params.get("alpha")
    alpha_c = params.get("alpha_c")
    c_max = params.get("c_max")
    c = params.get("c")

    optimal_power = sol.value(U)
    optimal_time = sol.value(T)
    pos = distance
    velocity = sol.value(X[0,:])
    w_bal = sol.value(X[1,:])

    # stats = sol.stats()
    # opt_time = stats['t_wall_total']

    max_power = 4*(alpha*w_bal + cp)*(c/(alpha_c*w_bal + c_max)*(1-c/(alpha_c*w_bal + c_max)))
    fig, ax = plt.subplots(3,1, figsize=(15,10))

    ax[0].set_title(f"The optimal time is {str(datetime.timedelta(seconds=round(optimal_time)))}")
    ax[0].set_ylabel("Power [W]")
    ax[0].set_ylim(0,max(max_power)+10)
    ax[0].plot(pos, max_power)
    ax[0].plot(pos, optimal_power)
    ax[0].plot(round(pos[-1])*[cp], color='tab:gray', linestyle='dashed')
    ax[0].legend(["Maximum attainable power", "Optimal power output", "CP"])
    ax1_twin = ax[0].twinx()
    ax1_twin.set_ylabel('Elevation [m]', color='tab:red')
    ax1_twin.plot(distance, elevation, color='tab:red')
    ax1_twin.tick_params(axis='y', labelcolor='tab:red')
    ax1_twin.legend(["Elevation Profile"])

    ax[1].set_ylabel("Velocity [m/s]")
    ax[1].set_ylim(0,20)
    ax[1].plot(pos, velocity)
    ax[1].legend(["Velocity"])
    ax2_twin = ax[1].twinx()
    ax2_twin.set_ylabel('Elevation [m]', color='tab:red')
    ax2_twin.plot(distance, elevation, color='tab:red')
    ax2_twin.tick_params(axis='y', labelcolor='tab:red')
    ax2_twin.legend(["Elevation Profile"])

    ax[2].set_ylabel("W'balance [J]")
    ax[2].set_xlabel("Position [m]")
    ax[2].set_ylim(0, 27500)
    ax[2].plot(pos, w_bal)
    ax[2].legend(["W'balance"])
    ax3_twin = ax[2].twinx()
    ax3_twin.set_ylabel('Elevation [m]', color='tab:red')
    ax3_twin.plot(distance, elevation, color='tab:red')
    ax3_twin.tick_params(axis='y', labelcolor='tab:red')
    ax3_twin.legend(["Elevation Profile"])

    fig.text(0.5, 0.02, f"Integration method: {opt_details.get('integration_method')}, points = {len(distance)}, N = {opt_details.get('N')}, W'balance model: {opt_details.get('w_bal_model')}, iterations: {opt_details.get('iterations')}, time: {str(datetime.timedelta(seconds=round(opt_details.get('opt_time'))))}", horizontalalignment="center")

    plt.show()