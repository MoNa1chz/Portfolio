"""
ตรวจจับ Emergent Failures: Feedback loops, Collusion, Mode collapse
"""
import statistics

class EmergentFailureDetector:
    
    def __init__(self):
        self.instance_counts = []        # สำหรับ feedback loop
        self.agent_decisions = {}        # สำหรับ collusion
        self.decision_history = []       # สำหรับ mode collapse
    
    # --- Failure 1: Feedback Loop ---
    def record_instance_count(self, count: int):
        self.instance_counts.append(count)
    
    def check_feedback_loop(self) -> bool:
        if len(self.instance_counts) < 5:
            return False
        recent = self.instance_counts[-10:]
        std = statistics.stdev(recent) if len(recent) > 1 else 0
        if std > 3:
            print(f"[FeedbackLoop] ⚠️  Instance count กระโดดผิดปกติ (σ={std:.1f})")
            return True
        return False
    
    # --- Failure 2: Collusion ---
    def record_agent_decision(self, agent: str, action: str):
        if agent not in self.agent_decisions:
            self.agent_decisions[agent] = []
        self.agent_decisions[agent].append(action)
    
    def check_collusion(self) -> bool:
        for agent, decisions in self.agent_decisions.items():
            if len(decisions) < 10:
                continue
            reject_rate = decisions.count("reject") / len(decisions)
            if reject_rate > 0.5:
                print(f"[Collusion] ⚠️  {agent} reject {reject_rate:.0%} — อาจเกิด collusion")
                return True
        return False
    
    # --- Failure 3: Mode Collapse ---
    def record_decision(self, action: str):
        self.decision_history.append(action)
    
    def check_mode_collapse(self) -> bool:
        if len(self.decision_history) < 10:
            return False
        recent = self.decision_history[-20:]
        most_common = max(set(recent), key=recent.count)
        rate = recent.count(most_common) / len(recent)
        if rate > 0.95:
            print(f"[ModeCollapse] ⚠️  {rate:.0%} ของ decisions เป็น '{most_common}'")
            return True
        return False
    
    def run_all_checks(self):
        print("\n[Monitor] === Emergent Failure Check ===")
        found = False
        if self.check_feedback_loop(): found = True
        if self.check_collusion():     found = True
        if self.check_mode_collapse(): found = True
        if not found:
            print("[Monitor] ✅ ไม่พบ emergent failures")


# ทดสอบ
if __name__ == "__main__":
    detector = EmergentFailureDetector()
    
    print("=== จำลอง Feedback Loop ===")
    # Instance count กระโดดขึ้นลงแบบ oscillate
    for count in [5, 10, 3, 12, 2, 15, 1, 14, 2, 13]:
        detector.record_instance_count(count)
    detector.check_feedback_loop()
    
    print("\n=== จำลอง Collusion ===")
    # Security agent reject ทุกอย่าง
    for _ in range(15):
        detector.record_agent_decision("security", "reject")
    for _ in range(2):
        detector.record_agent_decision("security", "accept")
    detector.check_collusion()
    
    print("\n=== จำลอง Mode Collapse ===")
    # ทุกการตัดสินใจเป็น reject
    for _ in range(18):
        detector.record_decision("reject")
    for _ in range(2):
        detector.record_decision("accept")
    detector.check_mode_collapse()
    
    print("\n=== รัน All Checks พร้อมกัน ===")
    detector.run_all_checks()