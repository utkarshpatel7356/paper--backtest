import numpy as np

class FairThompsonSampler:
    """
    A Multi-Armed Bandit that manages capital allocation across different strategies.
    It uses Beta distributions to estimate the success rate of each strategy.
    
    FAIRNESS CONSTRAINT: 
    Ensures that no strategy receives less than 'min_allocation' % of traffic/budget,
    preventing the system from starving potentially good but unlucky strategies.
    """
    def __init__(self, n_arms, min_allocation=0.05):
        self.n_arms = n_arms
        self.min_allocation = min_allocation # 5% minimum guarantee (Fairness)
        
        # Alpha (wins) and Beta (losses) for Beta distribution
        # We start with 1.0 to avoid division by zero (Uniform Prior)
        self.alpha = np.ones(n_arms)
        self.beta = np.ones(n_arms)
        
    def select_arm(self):
        """
        Samples from the posterior and applies Fairness constraints.
        """
        # 1. Thompson Sampling: Draw a random probability from each arm's distribution
        sampled_theta = np.random.beta(self.alpha, self.beta)
        
        # 2. Calculate Probabilities (Softmax-like allocation)
        # Instead of just picking the max, we want to allocate based on confidence
        total_theta = np.sum(sampled_theta)
        allocations = sampled_theta / total_theta
        
        # 3. Apply Fairness Constraint (The "Dr. Jain" Logic)
        # Clip allocations so everyone gets at least min_allocation
        allocations = np.maximum(allocations, self.min_allocation)
        
        # Re-normalize so they sum to 1.0
        allocations = allocations / np.sum(allocations)
        
        # 4. Choose one arm based on these fair probabilities
        chosen_arm = np.random.choice(self.n_arms, p=allocations)
        return chosen_arm, allocations

    def update(self, arm_index, reward):
        """
        Updates the belief for a specific arm.
        Reward should be binary (1=Profit, 0=Loss) or normalized between 0-1.
        """
        if reward > 0:
            self.alpha[arm_index] += 1  # Success!
        else:
            self.beta[arm_index] += 1   # Failure