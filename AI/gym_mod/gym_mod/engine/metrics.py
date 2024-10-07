import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

class metrics(object):
    def __init__(self, iters):
        self.loss = []
        self.reward = []
        self.iters = iters
        self.model_wins = 0
        
    def update_reward(self, add):
        self.reward.append(add)
        
    def update_loss(self, add):
        self.loss.append(add)
        
    def add_model_win(self):
        self.model_wins += 1
        
    def loss_curve(self):
        plt.title("Loss Curve")
        plt.xlabel("Counts")
        plt.ylabel("Loss")
        plt.plot(self.loss)
        plt.savefig("loss.png")
        plt.close()

    def reward_plot(self):
        y = lambda x, a, b: a*x+b
        x = np.arange(len(self.reward))
        popt, _ = curve_fit(y, x, self.reward)
        a, b = popt

        plt.title("Total Reward per episode")
        plt.xlabel("Epsiodes")
        plt.ylabel("Reward")
        plt.plot(self.reward)
        plt.plot(x, y(x, a, b))
        plt.savefig("reward.png")
        plt.close()

    def results(self):
        print("Model Won: ", self.model_wins)
        print("Enemy Won: ", self.iters - self.model_wins)
        res = input("Would you like to save the plots? (y/n): ")
        while True:
            if res.lower() == "y" or res.lower() == "yes":
                self.reward_plot()
                self.loss_curve()
                break
            elif res.lower() == 'n' or res.lower() == "no":
                break
            else:
                res = input("Not a valid input, try again (y/n): ")
