"""
Collective Budgets: Global constraints ที่ทุก agent ต้องอยู่ใน
"""

class CollectiveBudget:
    """ติดตาม rejection budget ของทุก agent รวมกัน"""
    
    AGENT_BUDGETS = {
        "security":   0.03,   # 3%
        "privacy":    0.01,   # 1%
        "compliance": 0.01,   # 1%
    }
    GLOBAL_MAX = 0.05         # 5% รวม
    
    def __init__(self):
        self.total_files = 0
        self.rejections = {"security": 0, "privacy": 0, "compliance": 0}
    
    def record_file(self):
        self.total_files += 1
    
    def can_reject(self, agent: str) -> bool:
        if self.total_files == 0:
            return True
        
        # ตรวจ agent budget
        agent_rate = self.rejections[agent] / self.total_files
        if agent_rate >= self.AGENT_BUDGETS[agent]:
            print(f"[Budget] ❌ {agent} เกิน budget ({agent_rate:.1%}/{self.AGENT_BUDGETS[agent]:.0%})")
            return False
        
        # ตรวจ global budget
        total_rejections = sum(self.rejections.values())
        global_rate = total_rejections / self.total_files
        if global_rate >= self.GLOBAL_MAX:
            print(f"[Budget] ❌ Global budget เกิน ({global_rate:.1%}/{self.GLOBAL_MAX:.0%})")
            return False
        
        return True
    
    def record_rejection(self, agent: str):
        self.rejections[agent] = self.rejections.get(agent, 0) + 1
        total = sum(self.rejections.values())
        global_rate = total / self.total_files if self.total_files else 0
        print(f"[Budget] 📊 {agent} reject → global rate: {global_rate:.1%}/{self.GLOBAL_MAX:.0%}")
    
    def status(self):
        print(f"\n[Budget] === Status ({self.total_files} files) ===")
        for agent, budget in self.AGENT_BUDGETS.items():
            used = self.rejections.get(agent, 0)
            rate = used / self.total_files if self.total_files else 0
            bar = "█" * int(rate * 100 / (budget * 100) * 10)
            print(f"  {agent:12} {rate:.1%}/{budget:.0%} {bar}")


class GlobalAnchorChecker:
    """ตรวจ system-level invariants หลัง agents ตัดสิน"""
    
    THROUGHPUT_MIN = 0.95  # ต้อง accept/flag อย่างน้อย 95%
    
    def __init__(self):
        self.results = []
    
    def record(self, action: str):
        self.results.append(action)
    
    def check_anchors(self) -> list[str]:
        violations = []
        if not self.results:
            return violations
        
        # Throughput anchor
        non_reject = sum(1 for r in self.results if r != "reject")
        throughput = non_reject / len(self.results)
        if throughput < self.THROUGHPUT_MIN:
            violations.append(
                f"THROUGHPUT ANCHOR VIOLATED: {throughput:.1%} < {self.THROUGHPUT_MIN:.0%}"
            )
        
        return violations


# ทดสอบ
if __name__ == "__main__":
    budget = CollectiveBudget()
    anchor = GlobalAnchorChecker()
    
    # จำลอง 20 files
    import random
    agents = ["security", "privacy", "compliance"]
    
    for i in range(20):
        budget.record_file()
        action = "accept"
        
        # สุ่ม rejection จาก agent
        agent = random.choice(agents)
        if random.random() < 0.15:   # 15% chance ลอง reject
            if budget.can_reject(agent):
                budget.record_rejection(agent)
                action = "reject"
                print(f"File {i+1:2}: {agent} → reject")
            else:
                action = "flag"       # budget หมด → flag แทน
                print(f"File {i+1:2}: {agent} → flag (budget หมด)")
        else:
            print(f"File {i+1:2}: accept")
        
        anchor.record(action)
    
    # สรุป
    budget.status()
    
    violations = anchor.check_anchors()
    if violations:
        print("\n[Anchor] ⚠️  VIOLATIONS:")
        for v in violations:
            print(f"  → {v}")
    else:
        print("\n[Anchor] ✅ ทุก global anchor ปลอดภัย")
        