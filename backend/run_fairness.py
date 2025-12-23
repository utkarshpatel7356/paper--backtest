import numpy as np
import matplotlib.pyplot as plt
from src.fairness.bandit import FairThompsonSampler

def simulate_market():
    print("⚖️ Initializing Fair Resource Allocation...")
    
    # Setup: 3 Strategies
    # Arm 0: High Risk (Win 60% of time, but volatile)
    # Arm 1: Stable (Win 55% of time, very consistent)
    # Arm 2: Bad Strategy (Win 40% of time)
    true_probabilities = [0.60, 0.55, 0.40]
    n_strategies = len(true_probabilities)
    
    # Initialize the Fair Bandit
    bandit = FairThompsonSampler(n_arms=n_strategies, min_allocation=0.10) # 10% Fairness Guarantee
    
    allocations_history = []
    rewards_history = []
    
    print("🚀 Running 1,000 Trading Days Simulation...")
    
    for t in range(1000):
        # 1. Bandit chooses which strategy to fund today
        chosen_arm, fair_weights = bandit.select_arm()
        
        # Record the "Fair Weights" to visualize allocation later
        allocations_history.append(fair_weights)
        
        # 2. Simulate Market Result (Bernoulli Trial)
        # Did the chosen strategy make money today?
        did_win = np.random.rand() < true_probabilities[chosen_arm]
        reward = 1 if did_win else 0
        
        # 3. Update Bandit's Belief
        bandit.update(chosen_arm, reward)
        rewards_history.append(reward)

    # --- Visualization ---
    alloc_data = np.array(allocations_history)
    
    plt.figure(figsize=(12, 6))
    
    # Plot Allocation Weights
    plt.subplot(1, 2, 1)
    plt.plot(alloc_data[:, 0], label="Strategy 0 (High Risk)", alpha=0.7)
    plt.plot(alloc_data[:, 1], label="Strategy 1 (Stable)", alpha=0.7)
    plt.plot(alloc_data[:, 2], label="Strategy 2 (Bad)", alpha=0.7)
    plt.axhline(y=0.10, color='r', linestyle='--', label="Fairness Floor (10%)")
    plt.title("Capital Allocation Evolution")
    plt.xlabel("Days")
    plt.ylabel("Percentage of Fund Allocated")
    plt.legend()
    
    # Plot Total Cumulative Regret (Optional math check)
    plt.subplot(1, 2, 2)
    cumulative_wins = np.cumsum(rewards_history)
    plt.plot(cumulative_wins, color='green')
    plt.title(f"Total Portfolio Wins: {cumulative_wins[-1]}")
    plt.xlabel("Days")
    
    plt.tight_layout()
    plt.show()
    
    print("✅ Simulation Complete. Check the graph.")
    print("Notice how Strategy 2 (Bad) never drops below 10% allocation?")
    print("That is the 'Fairness Constraint' preventing starvation.")

if __name__ == "__main__":
    simulate_market()