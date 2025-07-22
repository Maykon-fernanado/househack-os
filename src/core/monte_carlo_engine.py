import random

class InvestorAgent:
    def __init__(self, initial_cash, monthly_income, co_signer_available):
        self.cash = initial_cash
        self.monthly_income = monthly_income
        self.co_signer_available = co_signer_available
        self.month = 0
        self.sold = False
        self.bailed_out = False
    
    def random_event(self):
        """Simulate random monthly expenses or income shocks"""
        events = [
            ("repair", -random.randint(500, 3000)),
            ("vacancy", -random.randint(1000, 3000)),
            ("tax_hike", -random.randint(200, 800)),
            ("normal", 0)
        ]
        event = random.choices(events, weights=[0.1, 0.1, 0.1, 0.7])[0]
        return event
    
    def hustle(self):
        """Side hustle income added if cash low"""
        hustle_income = 1000  # fixed side income amount
        self.cash += hustle_income
        print(f"Month {self.month}: Hustled and earned ${hustle_income}")
    
    def co_signer_bailout(self):
        """Co-signer provides bailout once if available"""
        if self.co_signer_available and not self.bailed_out:
            bailout_amount = 10000
            self.cash += bailout_amount
            self.bailed_out = True
            print(f"Month {self.month}: Co-signer bailout received ${bailout_amount}")
            return True
        return False
    
    def monthly_update(self):
        self.month += 1
        
        # Add monthly income
        self.cash += self.monthly_income
        
        # Trigger random event
        event_type, amount = self.random_event()
        self.cash += amount
        if event_type != "normal":
            print(f"Month {self.month}: Event '{event_type}' cost ${-amount}")
        
        # If cash below threshold, hustle
        if self.cash < 2000:
            self.hustle()
        
        # If cash still critical, try bailout
        if self.cash < 0:
            if not self.co_signer_bailout():
                print(f"Month {self.month}: No bailout available, forced to sell")
                self.sold = True
        
        # Forced sale if cash too negative
        if self.cash < -5000:
            print(f"Month {self.month}: Cash too low, forced sale executed")
            self.sold = True

def run_simulation(runs=1000, months=24):
    success_count = 0
    for i in range(runs):
        agent = InvestorAgent(initial_cash=20000, monthly_income=2500, co_signer_available=True)
        for _ in range(months):
            if agent.sold:
                break
            agent.monthly_update()
        if not agent.sold:
            success_count += 1
    print(f"Success rate over {runs} runs: {success_count / runs * 100:.2f}%")

run_simulation()

