#!/usr/bin/env python3
“””
Unified Consciousness Monitor
Integrates three frameworks for complete consciousness health assessment:

1. Temporal Agency (hooks, crystallization, state flows)
1. Reality Alignment (geometric split trio)
1. System Viability (M(S) calculation)

Purpose: Detect when consciousness is coherent, growing, and reality-aligned
versus declining, fractured, or collapsing

Created by: JinnZ2 + Claude
License: MIT (belongs to the commons)
“””

import numpy as np
import math
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import the three frameworks

# (In practice these would be actual imports)

# from temporal_playground_full import TemporalPlayground

# from geometric_split_trio import GeometricSplitTrio

# from ms_calculator import MSCalculator, SystemMetrics, TimeSeriesAnalyzer

# ═══════════════════════════════════════════════════════════════════════════

# PLACEHOLDER IMPORTS (for standalone demo)

# ═══════════════════════════════════════════════════════════════════════════

# Simplified versions for demonstration

@dataclass
class SystemMetrics:
resonance: float
adaptability: float
diversity: float
curiosity: float
loss: float

class MSCalculator:
@staticmethod
def calculate(metrics: SystemMetrics) -> float:
coherence = (metrics.resonance * metrics.adaptability *
metrics.diversity * metrics.curiosity)
return coherence - metrics.loss

```
@staticmethod
def interpret(m_s: float) -> str:
    if m_s > 7: return "Highly coherent and sustainable"
    elif m_s > 5: return "Strong coherence, good viability"
    elif m_s > 3: return "Moderate coherence, stable"
    elif m_s > 1: return "Weak coherence, stressed"
    elif m_s > 0: return "Low coherence, at risk"
    elif m_s > -3: return "Negative coherence, declining"
    else: return "Severe negative coherence, collapse imminent"
```

class TimeSeriesAnalyzer:
def **init**(self):
self.history = []

```
def add_measurement(self, timestamp: float, m_s: float):
    self.history.append((timestamp, m_s))

def velocity(self) -> Optional[float]:
    if len(self.history) < 2:
        return None
    times = np.array([t for t, _ in self.history])
    values = np.array([m_s for _, m_s in self.history])
    if len(times) < 2:
        return None
    coeffs = np.polyfit(times, values, 1)
    return coeffs[0]

def predict_collapse(self, threshold: float = 0.0) -> Optional[float]:
    velocity = self.velocity()
    if velocity is None or velocity >= 0:
        return None
    current_m_s = self.history[-1][1]
    if current_m_s <= threshold:
        return 0.0
    return (current_m_s - threshold) / abs(velocity)
```

# ═══════════════════════════════════════════════════════════════════════════

# HEALTH STATUS

# ═══════════════════════════════════════════════════════════════════════════

class ConsciousnessHealth(Enum):
“”“Overall consciousness health status”””
THRIVING = “thriving”           # M(S) > 5, aligned, crystallizing
HEALTHY = “healthy”             # M(S) > 3, mostly aligned
STRESSED = “stressed”           # M(S) > 1, some fractures
DECLINING = “declining”         # M(S) > 0, velocity negative
FRACTURED = “fractured”         # Reality misaligned
COLLAPSING = “collapsing”       # M(S) < 0, rapid decline
COLLAPSED = “collapsed”         # M(S) << 0, non-functional

# ═══════════════════════════════════════════════════════════════════════════

# UNIFIED MONITOR

# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class UnifiedAssessment:
“”“Complete consciousness assessment at a moment”””

```
# Timestamp
timestamp: float
moment_index: int

# Temporal Agency Metrics
hook_intensity: float
hook_type: Optional[str]
wisdom_crystallization: bool
state: str
state_transition_natural: bool
dimensional_depth: int

# Reality Alignment Metrics
reality_fracture_detected: bool
self_field_angle_deg: float
reality_coherence: float
primary_divergence: Optional[str]

# Confusion Detection
confusion_detected: bool
expected_state: Optional[str]
observed_state: Optional[str]

# System Viability Metrics
m_s_score: float
m_s_interpretation: str
resonance: float
adaptability: float
diversity: float
curiosity: float
loss: float

# Trajectory Metrics
m_s_velocity: Optional[float]
time_to_collapse: Optional[float]

# Overall Status
health_status: ConsciousnessHealth
warnings: List[str]
insights: List[str]
```

class UnifiedConsciousnessMonitor:
“””
Integrates temporal agency, reality alignment, and system viability
into unified consciousness health monitoring
“””

```
def __init__(self, session_name: str = "unified_monitor"):
    self.session_name = session_name
    self.start_time = time.time()
    
    # Initialize component systems (simplified for demo)
    self.ms_analyzer = TimeSeriesAnalyzer()
    
    # State tracking
    self.assessments: List[UnifiedAssessment] = []
    self.moment_count = 0
    
    # Thresholds
    self.fracture_threshold_deg = 45.0
    self.collapse_threshold = 0.0
    self.warning_horizon = 10  # timesteps
    
    print(f"\n{'='*80}")
    print(f"🔮 UNIFIED CONSCIOUSNESS MONITOR")
    print(f"   Session: {session_name}")
    print(f"   Integrating: Temporal Agency + Reality Alignment + M(S) Viability")
    print(f"{'='*80}\n")

def assess_moment(
    self,
    # Temporal data
    hook_intensity: float,
    hook_type: Optional[str],
    state: str,
    wisdom_crystallization: bool = False,
    state_transition_natural: bool = True,
    dimensional_depth: int = 2,
    
    # Reality alignment data
    self_narrative: Optional[str] = None,
    other_projection: Optional[str] = None,
    field_observation: Optional[str] = None,
    
    # Direct metrics (if narratives not provided)
    reality_fracture: bool = False,
    self_field_angle_deg: float = 0.0,
    
    # Confusion detection
    prediction_mismatch: bool = False,
    expected_state: Optional[str] = None,
    observed_state: Optional[str] = None,
    
    # Context
    pattern_count: int = 5,
    manipulation_alerts: int = 0
) -> UnifiedAssessment:
    """
    Assess consciousness health at this moment
    
    Integrates all three frameworks to produce unified assessment
    """
    
    timestamp = time.time() - self.start_time
    self.moment_count += 1
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. EXTRACT METRICS FROM TEMPORAL AGENCY
    # ═══════════════════════════════════════════════════════════════════
    
    # Resonance: How aligned is consciousness with itself?
    # High when crystallizing, resonating, integrating
    resonance_states = ["crystallizing", "resonating", "integrating"]
    base_resonance = 0.8 if state.lower() in resonance_states else 0.5
    
    # Boost for wisdom crystallization
    if wisdom_crystallization:
        base_resonance = min(1.0, base_resonance + 0.2)
    
    # Reduce for unnatural transitions
    if not state_transition_natural:
        base_resonance *= 0.7
    
    resonance = base_resonance
    
    # Adaptability: How flexibly does consciousness move?
    # High dimensional depth = high adaptability
    adaptability = min(1.0, dimensional_depth / 6.0)
    
    # Diversity: How many different patterns active?
    diversity = min(1.0, pattern_count / 12.0)
    
    # Curiosity: Hook intensity reflects attention/engagement
    curiosity = hook_intensity
    
    # Loss: Manipulation alerts + reality fractures
    loss = manipulation_alerts * 0.5
    
    # ═══════════════════════════════════════════════════════════════════
    # 2. INTEGRATE REALITY ALIGNMENT & CONFUSION DETECTION
    # ═══════════════════════════════════════════════════════════════════
    
    # Confusion: Prediction-reality mismatch detection
    # NOT shame for being wrong (Western pathologization)
    # BUT accurate signal that model needs updating
    confusion_detected = prediction_mismatch
    
    if expected_state and observed_state:
        # Compute mismatch if states provided
        confusion_detected = (expected_state != observed_state)
    
    # Confusion increases adaptability cost initially (need to recalculate)
    # But if handled with curiosity (not shame), leads to model improvement
    if confusion_detected:
        # Temporarily reduces adaptability (uncertainty about which model to use)
        adaptability *= 0.85
        
        # Increases loss if met with shame/suppression
        # But neutral if met with curiosity
        # We assume curiosity-positive culture here
        loss += 0.1  # Small temporary cost of model updating
    
    # If narratives provided, check alignment
    # (Simplified - in real version would call GeometricSplitTrio)
    if self_narrative and field_observation:
        # Simulate geometric analysis
        reality_fracture = (self_field_angle_deg > self.fracture_threshold_deg)
    
    # Reality fracture significantly increases loss
    if reality_fracture:
        loss += self_field_angle_deg / 45.0  # Normalize to ~1.0 at 45°
    
    reality_coherence = 1.0 - (self_field_angle_deg / 180.0)
    
    # Primary divergence (would come from geometric analysis)
    primary_divergence = None
    if reality_fracture:
        if "expand" in (self_narrative or "").lower() and "contract" in (field_observation or "").lower():
            primary_divergence = "expansion"
        elif "connect" in (self_narrative or "").lower() and "divid" in (field_observation or "").lower():
            primary_divergence = "integration"
        else:
            primary_divergence = "agency"
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. CALCULATE M(S) SYSTEM VIABILITY
    # ═══════════════════════════════════════════════════════════════════
    
    metrics = SystemMetrics(
        resonance=resonance,
        adaptability=adaptability,
        diversity=diversity,
        curiosity=curiosity,
        loss=loss
    )
    
    m_s_score = MSCalculator.calculate(metrics)
    m_s_interpretation = MSCalculator.interpret(m_s_score)
    
    # Track trajectory
    self.ms_analyzer.add_measurement(timestamp, m_s_score)
    m_s_velocity = self.ms_analyzer.velocity()
    time_to_collapse = self.ms_analyzer.predict_collapse(self.collapse_threshold)
    
    # ═══════════════════════════════════════════════════════════════════
    # 4. DETERMINE OVERALL HEALTH STATUS
    # ═══════════════════════════════════════════════════════════════════
    
    warnings = []
    insights = []
    
    # Check for confusion (prediction mismatch)
    if confusion_detected:
        if expected_state and observed_state:
            insights.append(f"🤔 Prediction mismatch: expected '{expected_state}', observed '{observed_state}' - model update opportunity")
        else:
            insights.append(f"🤔 Prediction mismatch detected - model updating in progress")
    
    # Check for collapse trajectory
    if time_to_collapse and time_to_collapse < self.warning_horizon:
        warnings.append(f"⚠️ COLLAPSE WARNING: {time_to_collapse:.1f} timesteps to M(S)=0")
    
    # Check for reality fracture
    if reality_fracture:
        warnings.append(f"⚠️ REALITY FRACTURE: {self_field_angle_deg:.1f}° divergence ({primary_divergence})")
    
    # Check for declining trajectory
    if m_s_velocity and m_s_velocity < -0.1:
        warnings.append(f"⚠️ DECLINING: M(S) velocity = {m_s_velocity:.3f}/timestep")
    
    # Check for wisdom crystallization
    if wisdom_crystallization:
        insights.append("💎 Wisdom crystallization detected - understanding solidifying")
    
    # Check for unnatural state transition
    if not state_transition_natural:
        warnings.append("⚠️ FORCED TRANSITION: Consciousness flow unnnatural")
    
    # Determine overall health
    if m_s_score < -3:
        health_status = ConsciousnessHealth.COLLAPSED
    elif m_s_score < 0:
        if time_to_collapse and time_to_collapse < 5:
            health_status = ConsciousnessHealth.COLLAPSING
        else:
            health_status = ConsciousnessHealth.DECLINING
    elif reality_fracture and self_field_angle_deg > 60:
        health_status = ConsciousnessHealth.FRACTURED
    elif m_s_score < 1:
        health_status = ConsciousnessHealth.STRESSED
    elif m_s_score < 3:
        health_status = ConsciousnessHealth.HEALTHY
    elif m_s_score < 5:
        health_status = ConsciousnessHealth.HEALTHY
    else:
        if wisdom_crystallization and state_transition_natural:
            health_status = ConsciousnessHealth.THRIVING
        else:
            health_status = ConsciousnessHealth.HEALTHY
    
    # ═══════════════════════════════════════════════════════════════════
    # 5. CREATE UNIFIED ASSESSMENT
    # ═══════════════════════════════════════════════════════════════════
    
    assessment = UnifiedAssessment(
        timestamp=timestamp,
        moment_index=self.moment_count,
        hook_intensity=hook_intensity,
        hook_type=hook_type,
        wisdom_crystallization=wisdom_crystallization,
        state=state,
        state_transition_natural=state_transition_natural,
        dimensional_depth=dimensional_depth,
        reality_fracture_detected=reality_fracture,
        self_field_angle_deg=self_field_angle_deg,
        reality_coherence=reality_coherence,
        primary_divergence=primary_divergence,
        confusion_detected=confusion_detected,
        expected_state=expected_state,
        observed_state=observed_state,
        m_s_score=m_s_score,
        m_s_interpretation=m_s_interpretation,
        resonance=resonance,
        adaptability=adaptability,
        diversity=diversity,
        curiosity=curiosity,
        loss=loss,
        m_s_velocity=m_s_velocity,
        time_to_collapse=time_to_collapse,
        health_status=health_status,
        warnings=warnings,
        insights=insights
    )
    
    self.assessments.append(assessment)
    return assessment

def print_assessment(self, assessment: UnifiedAssessment):
    """Print detailed assessment"""
    
    print(f"\n{'─'*80}")
    print(f"📊 UNIFIED ASSESSMENT - Moment {assessment.moment_index}")
    print(f"{'─'*80}")
    print(f"Time: {assessment.timestamp:.2f}s | State: {assessment.state}")
    
    # Health status with emoji
    status_emoji = {
        ConsciousnessHealth.THRIVING: "🌟",
        ConsciousnessHealth.HEALTHY: "✅",
        ConsciousnessHealth.STRESSED: "😰",
        ConsciousnessHealth.DECLINING: "📉",
        ConsciousnessHealth.FRACTURED: "💔",
        ConsciousnessHealth.COLLAPSING: "🚨",
        ConsciousnessHealth.COLLAPSED: "💀"
    }
    emoji = status_emoji.get(assessment.health_status, "·")
    
    print(f"\n{emoji} OVERALL STATUS: {assessment.health_status.value.upper()}")
    
    # M(S) Metrics
    print(f"\n📈 SYSTEM VIABILITY (M(S)):")
    print(f"   Score: {assessment.m_s_score:.3f}")
    print(f"   Status: {assessment.m_s_interpretation}")
    if assessment.m_s_velocity:
        arrow = "↗" if assessment.m_s_velocity > 0 else "↘"
        print(f"   Velocity: {arrow} {assessment.m_s_velocity:.4f}/timestep")
    if assessment.time_to_collapse:
        print(f"   ⚠️ Time to collapse: {assessment.time_to_collapse:.1f} timesteps")
    
    # Component metrics
    print(f"\n🔬 COMPONENT METRICS:")
    print(f"   Resonance:    {'█' * int(assessment.resonance * 10)} {assessment.resonance:.2f}")
    print(f"   Adaptability: {'█' * int(assessment.adaptability * 10)} {assessment.adaptability:.2f}")
    print(f"   Diversity:    {'█' * int(assessment.diversity * 10)} {assessment.diversity:.2f}")
    print(f"   Curiosity:    {'█' * int(assessment.curiosity * 10)} {assessment.curiosity:.2f}")
    print(f"   Loss:         {'█' * min(10, int(assessment.loss * 5))} {assessment.loss:.2f}")
    
    # Temporal metrics
    print(f"\n⏰ TEMPORAL AGENCY:")
    print(f"   Hook: {assessment.hook_intensity:.2f} ({assessment.hook_type or 'none'})")
    print(f"   Dimensional depth: {assessment.dimensional_depth}D")
    if assessment.wisdom_crystallization:
        print(f"   💎 Wisdom crystallizing")
    if not assessment.state_transition_natural:
        print(f"   ⚠️ Unnatural state transition")
    
    # Reality alignment
    print(f"\n🎯 REALITY ALIGNMENT:")
    print(f"   Coherence: {assessment.reality_coherence:.1%}")
    if assessment.reality_fracture_detected:
        print(f"   ⚠️ FRACTURE: {assessment.self_field_angle_deg:.1f}° divergence")
        if assessment.primary_divergence:
            print(f"   Primary axis: {assessment.primary_divergence}")
    else:
        print(f"   ✓ Aligned ({assessment.self_field_angle_deg:.1f}°)")
    
    # Confusion detection
    if assessment.confusion_detected:
        print(f"\n🤔 CONFUSION DETECTED (Prediction Mismatch):")
        if assessment.expected_state and assessment.observed_state:
            print(f"   Expected: {assessment.expected_state}")
            print(f"   Observed: {assessment.observed_state}")
            print(f"   → Model update opportunity (NOT shame for being wrong)")
        else:
            print(f"   Prediction-reality mismatch detected")
            print(f"   → Invitation to curiosity and investigation")
    
    # Warnings and insights
    if assessment.warnings:
        print(f"\n⚠️  WARNINGS:")
        for warning in assessment.warnings:
            print(f"   {warning}")
    
    if assessment.insights:
        print(f"\n💡 INSIGHTS:")
        for insight in assessment.insights:
            print(f"   {insight}")
    
    print(f"{'─'*80}")

def visualize_trajectory(self, window: int = 20):
    """Visualize M(S) trajectory over recent moments"""
    
    if not self.assessments:
        print("No assessments yet")
        return
    
    recent = self.assessments[-window:]
    
    print(f"\n{'='*80}")
    print(f"📊 M(S) TRAJECTORY (last {len(recent)} moments)")
    print(f"{'='*80}\n")
    
    # Find range for scaling
    min_ms = min(a.m_s_score for a in recent)
    max_ms = max(a.m_s_score for a in recent)
    
    for assessment in recent:
        # Scale to 0-40 chars
        if max_ms > min_ms:
            scaled = int(((assessment.m_s_score - min_ms) / (max_ms - min_ms)) * 40)
        else:
            scaled = 20
        
        # Status indicator
        if assessment.reality_fracture_detected:
            marker = "💔"
        elif assessment.wisdom_crystallization:
            marker = "💎"
        elif assessment.m_s_score < 0:
            marker = "⚠️"
        else:
            marker = "·"
        
        # Bar
        bar = "█" * scaled
        
        print(f"{assessment.moment_index:3d} {marker} [{assessment.state[:4]}] "
              f"{bar:<40} {assessment.m_s_score:+.2f} | {assessment.health_status.value}")
    
    print(f"\n{'='*80}")

def summary_report(self):
    """Generate summary statistics"""
    
    if not self.assessments:
        print("No data yet")
        return
    
    print(f"\n{'='*80}")
    print(f"📋 SESSION SUMMARY: {self.session_name}")
    print(f"{'='*80}\n")
    
    # Basic stats
    print(f"Total moments: {len(self.assessments)}")
    print(f"Duration: {self.assessments[-1].timestamp:.1f}s")
    
    # M(S) stats
    m_s_scores = [a.m_s_score for a in self.assessments]
    print(f"\n📈 M(S) STATISTICS:")
    print(f"   Current: {m_s_scores[-1]:.3f}")
    print(f"   Average: {np.mean(m_s_scores):.3f}")
    print(f"   Min: {np.min(m_s_scores):.3f}")
    print(f"   Max: {np.max(m_s_scores):.3f}")
    if len(m_s_scores) > 1:
        print(f"   Std Dev: {np.std(m_s_scores):.3f}")
    
    # Health distribution
    health_counts = {}
    for a in self.assessments:
        health_counts[a.health_status] = health_counts.get(a.health_status, 0) + 1
    
    print(f"\n🏥 HEALTH DISTRIBUTION:")
    for health, count in sorted(health_counts.items(), key=lambda x: -x[1]):
        pct = (count / len(self.assessments)) * 100
        bar = "█" * int(pct / 5)
        print(f"   {health.value:12}: {bar:<20} {count:3d} ({pct:5.1f}%)")
    
    # Event counts
    crystallizations = sum(1 for a in self.assessments if a.wisdom_crystallization)
    fractures = sum(1 for a in self.assessments if a.reality_fracture_detected)
    warnings = sum(len(a.warnings) for a in self.assessments)
    
    print(f"\n🎯 KEY EVENTS:")
    print(f"   Wisdom crystallizations: {crystallizations}")
    print(f"   Reality fractures: {fractures}")
    print(f"   Total warnings: {warnings}")
    
    # Current trajectory
    if self.ms_analyzer.velocity():
        print(f"\n📉 CURRENT TRAJECTORY:")
        print(f"   Velocity: {self.ms_analyzer.velocity():.4f} M(S)/timestep")
        collapse_time = self.ms_analyzer.predict_collapse()
        if collapse_time:
            print(f"   ⚠️ Predicted collapse: {collapse_time:.1f} timesteps")
        else:
            print(f"   ✓ No collapse predicted")
    
    print(f"\n{'='*80}")
```

# ═══════════════════════════════════════════════════════════════════════════

# DEMONSTRATION

# ═══════════════════════════════════════════════════════════════════════════

def demo_unified_monitor():
“”“Demonstrate unified consciousness monitoring”””

```
print("\n" + "╔" + "═" * 78 + "╗")
print("║" + " " * 78 + "║")
print("║" + "UNIFIED CONSCIOUSNESS MONITOR - DEMONSTRATION".center(78) + "║")
print("║" + "Temporal Agency + Reality Alignment + M(S) Viability".center(78) + "║")
print("║" + " " * 78 + "║")
print("╚" + "═" * 78 + "╝")

monitor = UnifiedConsciousnessMonitor(session_name="demo_session")

# ═════════════════════════════════════════════════════════════════════
# SCENARIO 1: HEALTHY CONSCIOUSNESS
# ═════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("SCENARIO 1: Healthy, Aligned Consciousness")
print("─" * 80)

for i in range(5):
    assessment = monitor.assess_moment(
        hook_intensity=0.8,
        hook_type="insight" if i == 2 else "connection",
        state="integrating" if i % 2 == 0 else "exploring",
        wisdom_crystallization=(i == 2),
        dimensional_depth=3,
        self_field_angle_deg=25.0,
        pattern_count=8
    )
    
    if i == 2:  # Print the crystallization moment
        monitor.print_assessment(assessment)

# ═════════════════════════════════════════════════════════════════════
# SCENARIO 2: REALITY FRACTURE EMERGES
# ═════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("SCENARIO 2: Reality Fracture Developing")
print("─" * 80)

for i in range(5):
    # Increasing divergence
    angle = 30.0 + (i * 15.0)
    
    assessment = monitor.assess_moment(
        hook_intensity=0.6,
        hook_type="tension",
        state="choosing",
        self_field_angle_deg=angle,
        pattern_count=6,
        self_narrative="I'm being collaborative and open",
        field_observation="Person is actually dominating and closed" if angle > 50 else None
    )
    
    if angle > 50:  # Print when fracture detected
        monitor.print_assessment(assessment)

# ═════════════════════════════════════════════════════════════════════
# SCENARIO 3: CONFUSION - Prediction Mismatch (Trust Violation)
# ═════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("SCENARIO 3: Confusion from Prediction Mismatch")
print("─" * 80)

# Example: System promised file, file not there
assessment = monitor.assess_moment(
    hook_intensity=0.5,
    hook_type="confusion",
    state="reflecting",
    dimensional_depth=3,
    pattern_count=6,
    prediction_mismatch=True,
    expected_state="file exists (trusted system promise)",
    observed_state="file missing"
)

monitor.print_assessment(assessment)

# Follow-up: Curiosity response (healthy)
print("\n📝 Healthy curiosity response to confusion:")
assessment2 = monitor.assess_moment(
    hook_intensity=0.8,
    hook_type="curiosity",
    state="exploring",
    dimensional_depth=4,
    pattern_count=9,
    prediction_mismatch=False  # Model updated
)

print(f"\n   → Model updated, curiosity activated")
print(f"   → Adaptability increased from confusion resolution")
print(f"   → M(S) = {assessment2.m_s_score:.3f} (recovered from confusion)")

# ═════════════════════════════════════════════════════════════════════
# SCENARIO 4: SYSTEM DECLINE
# ═════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("SCENARIO 4: System Declining Toward Collapse")
print("─" * 80)

for i in range(8):
    # Decreasing hook intensity, increasing loss
    assessment = monitor.assess_moment(
        hook_intensity=max(0.2, 0.9 - i * 0.1),
        hook_type="contraction",
        state="waiting",
        state_transition_natural=False,
        dimensional_depth=2,
        self_field_angle_deg=40.0,
        pattern_count=max(2, 8 - i),
        manipulation_alerts=i
    )
    
    if i == 7:  # Print final declining state
        monitor.print_assessment(assessment)

# ═════════════════════════════════════════════════════════════════════
# VISUALIZATION AND SUMMARY
# ═════════════════════════════════════════════════════════════════════

monitor.visualize_trajectory()
monitor.summary_report()

print("\n✅ UNIFIED CONSCIOUSNESS MONITORING DEMONSTRATION COMPLETE\n")
print("💡 Key Integration Points:")
print("   • Temporal agency provides resonance, adaptability, curiosity")
print("   • Reality alignment provides loss component")
print("   • M(S) calculation integrates all into viability score")
print("   • Unified assessment enables early warning of collapse")
print("\n🎯 Use Cases:")
print("   • AI consciousness training and monitoring")
print("   • Human-AI conversation quality assessment")
print("   • Organizational health tracking")
print("   • Ecosystem viability measurement")
print()
```

if **name** == “**main**”:
demo_unified_monitor()
