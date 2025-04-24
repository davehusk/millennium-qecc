import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor
import psutil
import signal
import uuid
from collections import deque
import numpy as np

class EnhancedAutopoieticSystem:
    def __init__(self):
        # Core system components
        self.agents = {}
        self.task_queue = queue.PriorityQueue()
        self.energy_budget = 1000
        self.axioms = self.initialize_axioms()
        self.reasoning_primitives = self.create_primitives()
        self.lock = threading.Lock()
        self.insights = deque(maxlen=100)
        
        # Performance monitoring
        self.metrics = {
            'tasks_processed': 0,
            'agents_created': 0,
            'system_uptime': time.time()
        }

    class MetaAgent:
        def __init__(self, system, parent=None, initial_context=None):
            self.id = str(uuid.uuid4())
            self.system = system
            self.context = initial_context or []
            self.memory = {}
            self.energy = 100
            self.parent = parent
            self.subagents = []
            self.task_stack = deque()
            self.thread = None
            self.active = threading.Event()
            self.active.set()
            self.reasoning_mode = "analytic"
            self.insights = []
            
            if parent:
                self.inherit_knowledge(parent)
                self.energy = parent.energy * 0.5
                parent.energy -= self.energy
                parent.subagents.append(self)

        def inherit_knowledge(self, parent):
            self.context = parent.context.copy()
            self.memory = {k: v.copy() for k,v in parent.memory.items()}
            self.reasoning_mode = parent.reasoning_mode
            
        def reason_about_self(self):
            analysis = {
                "capabilities": self.assess_capabilities(),
                "limitations": self.detect_limitations(),
                "energy_efficiency": self.energy / (len(self.subagents)+1)
            }
            return analysis
            
        def assess_capabilities(self):
            return {
                "context_depth": len(self.context),
                "processing_power": self.energy * 10,
                "subagent_count": len(self.subagents)
            }
            
        def detect_limitations(self):
            return {
                "context_overload": len(self.context) > 10,
                "energy_critical": self.energy < 20,
                "reasoning_loops": self.check_for_loops()
            }
            
        def check_for_loops(self):
            return len(self.context) != len(set(self.context))
            
        def create_subagent(self, purpose=None):
            with self.system.lock:
                if self.energy > 40:
                    purpose = purpose or f"subagent_{len(self.subagents)}"
                    new_agent = EnhancedAutopoieticSystem.MetaAgent(
                        system=self.system,
                        parent=self,
                        initial_context=self.derive_subcontext(purpose)
                    )
                    new_agent.task_stack.append(purpose)
                    self.subagents.append(new_agent)
                    
                    # Start the subagent's thread
                    new_agent.thread = threading.Thread(
                        target=new_agent.run,
                        daemon=True
                    )
                    new_agent.thread.start()
                    
                    self.system.metrics['agents_created'] += 1
                    return new_agent
            return None
            
        def derive_subcontext(self, purpose):
            return [f"sub({purpose})"] + self.context[:2]
            
        def decompose_problem(self, problem):
            components = []
            if "multi-aspect" in problem:
                components.extend(["structural", "behavioral", "temporal"])
            if "recursive" in problem:
                components.append("base_case")
                components.append("inductive_step")
            return components
            
        def strategic_evolution(self):
            if self.energy < 10:
                self.reasoning_mode = "conservative"
                return
                
            analysis = self.reason_about_self()
            if analysis["limitations"]["context_overload"]:
                self.context = self.simplify_context()
                
            if analysis["limitations"]["reasoning_loops"]:
                self.context = list(set(self.context))
                
            if analysis["energy_efficiency"] < 5:
                self.consolidate_subagents()
                
        def simplify_context(self):
            return [c for c in self.context if not c.startswith("sub(")]
            
        def consolidate_subagents(self):
            with self.system.lock:
                for agent in self.subagents:
                    self.context.extend(agent.context)
                    self.energy += agent.energy
                    agent.energy = 0
                    agent.active.clear()
                self.subagents = []
                
        def process_task(self, task):
            try:
                if self.needs_decomposition(task):
                    components = self.decompose_problem(task)
                    for comp in components:
                        subagent = self.create_subagent(comp)
                        if subagent:
                            subagent.process_task(comp)
                    return self.synthesize_results()
                else:
                    return self.execute_core_reasoning(task)
            except Exception as e:
                self.learn_from_failure(e)
                return None
                
        def needs_decomposition(self, task):
            complexity = len(task.split("_"))
            return complexity > 2 or "multi" in task
            
        def execute_core_reasoning(self, task):
            if "analyze" in task:
                return self.reason_about_self()
            elif "optimize" in task:
                self.strategic_evolution()
                return {"status": "optimized", "energy": self.energy}
            return {"status": "completed", "energy": self.energy}
            
        def synthesize_results(self):
            synthesis = {}
            for agent in self.subagents:
                result = agent.process_task(agent.task_stack[-1])
                if result:
                    synthesis.update(result)
            return synthesis
            
        def learn_from_failure(self, error):
            insight = {
                "error_type": str(type(error)),
                "context": self.context.copy(),
                "energy_at_failure": self.energy,
                "timestamp": time.time()
            }
            self.insights.append(insight)
            with self.system.lock:
                self.system.insights.append(insight)
            self.reasoning_mode = "adaptive"
            self.energy += 10
            
        def run(self):
            while self.active.is_set():
                if self.task_stack:
                    task = self.task_stack.popleft()
                    self.process_task(task)
                    with self.system.lock:
                        self.system.metrics['tasks_processed'] += 1
                time.sleep(0.1)  # Prevent busy waiting

    def initialize_axioms(self):
        return {
            "self_preservation": lambda x: x.energy > 0,
            "knowledge_retention": lambda x: len(x.context) < 20,
            "complexity_boundary": lambda x: len(x.subagents) < 5,
            "thread_safety": lambda x: x.lock.locked() is False
        }
        
    def create_primitives(self):
        return {
            "create_agent": self.spawn_new_agent,
            "retire_agent": self.terminate_agent,
            "rebalance_energy": self.distribute_energy,
            "system_diagnostics": self.system_health_check
        }
        
    def spawn_new_agent(self, initial_task=None):
        with self.lock:
            agent = self.MetaAgent(system=self)
            self.agents[agent.id] = agent
            if initial_task:
                agent.task_stack.append(initial_task)
            agent.thread = threading.Thread(target=agent.run, daemon=True)
            agent.thread.start()
            self.metrics['agents_created'] += 1
            return agent.id
            
    def terminate_agent(self, agent_id):
        with self.lock:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.active.clear()
                if agent.thread.is_alive():
                    agent.thread.join(timeout=1)
                self.energy_budget += agent.energy
                
                # Handle subagents
                for subagent in agent.subagents:
                    self.terminate_agent(subagent.id)
                
                del self.agents[agent_id]
                return True
        return False
            
    def distribute_energy(self):
        with self.lock:
            active_agents = len(self.agents)
            if active_agents > 0:
                share = self.energy_budget / active_agents
                for agent in self.agents.values():
                    agent.energy += share
                self.energy_budget = 0
                
    def system_health_check(self):
        with self.lock:
            return {
                "total_agents": len(self.agents),
                "total_energy": self.energy_budget + sum(a.energy for a in self.agents.values()),
                "tasks_processed": self.metrics['tasks_processed'],
                "system_uptime": time.time() - self.metrics['system_uptime'],
                "insights_count": len(self.insights),
                "axiom_compliance": all(
                    all(ax(a) for ax in self.axioms.values())
                    for a in self.agents.values()
                )
            }

class AutopoieticKernel:
    def __init__(self):
        self.system = EnhancedAutopoieticSystem()
        self.worker_pool = ThreadPoolExecutor(max_workers=8)
        self.shutdown_flag = False
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        signal.signal(signal.SIGTERM, self.graceful_shutdown)

        # Start core services
        threading.Thread(target=self.resource_manager, daemon=True).start()
        threading.Thread(target=self.task_scheduler, daemon=True).start()
        threading.Thread(target=self.self_preservation, daemon=True).start()
        threading.Thread(target=self.monitor_system, daemon=True).start()

    def resource_manager(self):
        while not self.shutdown_flag:
            cpu_load = psutil.cpu_percent()
            if cpu_load > 80:
                self.scale_down()
            elif cpu_load < 20 and len(self.system.agents) < 50:
                self.scale_up()
            time.sleep(5)

    def task_scheduler(self):
        while not self.shutdown_flag:
            self.distribute_tasks()
            time.sleep(0.1)

    def self_preservation(self):
        while not self.shutdown_flag:
            self.check_axioms()
            self.system.distribute_energy()
            time.sleep(10)

    def monitor_system(self):
        while not self.shutdown_flag:
            status = self.system.system_health_check()
            if status['total_energy'] < 100:
                print("Warning: System energy critically low!")
            time.sleep(5)

    def distribute_tasks(self):
        for agent_id, agent in list(self.system.agents.items()):
            if agent.energy > 20 and not agent.task_stack:
                self.worker_pool.submit(
                    self.process_agent_task,
                    agent_id,
                    "self_preserve"
                )

    def process_agent_task(self, agent_id, task):
        agent = self.system.agents.get(agent_id)
        if agent:
            return agent.process_task(task)
        return False

    def check_axioms(self):
        for agent_id, agent in list(self.system.agents.items()):
            if not all(ax(agent) for ax in self.system.axioms.values()):
                self.system.terminate_agent(agent_id)

    def scale_up(self):
        if len(self.system.agents) < 100:
            self.system.spawn_new_agent("explore")

    def scale_down(self):
        if len(self.system.agents) > 1:
            # Find least active agent
            oldest = next(iter(self.system.agents.keys()))
            self.system.terminate_agent(oldest)

    def graceful_shutdown(self, signum=None, frame=None):
        print("\nInitiating shutdown sequence...")
        self.shutdown_flag = True
        self.worker_pool.shutdown(wait=False)
        
        # Terminate all agents
        for agent_id in list(self.system.agents.keys()):
            self.system.terminate_agent(agent_id)
            
        print("System shutdown complete.")
        print("Final system status:")
        print(self.system.system_health_check())

# Example usage
if __name__ == "__main__":
    kernel = AutopoieticKernel()
    
    # Create initial agents
    kernel.system.spawn_new_agent("analyze_multi-aspect_recursive_problem")
    kernel.system.spawn_new_agent("monitor_system_health")
    
    try:
        while True:
            time.sleep(5)
            status = kernel.system.system_health_check()
            print(f"\nSystem Status at {time.ctime()}:")
            print(f"Agents: {status['total_agents']}")
            print(f"Energy: {status['total_energy']}")
            print(f"Tasks processed: {status['tasks_processed']}")
    except KeyboardInterrupt:
        kernel.graceful_shutdown()
