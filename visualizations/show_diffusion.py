import matplotlib.pyplot as plt
import numpy as np
from src.models.diffusion import BassDiffusionModel


if __name__ == "__main__":
    model = BassDiffusionModel(
        market_potential=8000,
        p=0.03,
        q=0.38,
        dt=1.0,
        initial_adopters=900,
    )

    model.run(steps=50)

    t = np.array(model.history_time)
    N = np.array(model.history_N)
    new_adopters = np.array(model.history_new_adopters)

    # 1) Cumulative adoption over time
    plt.figure()
    plt.plot(t, N, marker="o")
    plt.xlabel("Time")
    plt.ylabel("Cumulative adopters N(t)")
    plt.title("Bass diffusion – cumulative adoption")
    plt.tight_layout()

    # 2) New adopters per period
    plt.figure()
    plt.bar(t, new_adopters, width=0.8)
    plt.xlabel("Time")
    plt.ylabel("New adopters per step")
    plt.title("Bass diffusion – new adopters per period")
    plt.tight_layout()

    plt.show()
