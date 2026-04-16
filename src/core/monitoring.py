class MonitoringAlert:
    """
    MonitoringAlert: Tracks metrics from various safety layers and fires 
    alerts when certain thresholds are exceeded.
    
    This is critical for detecting systematic attacks or performance degradation.
    """
    def __init__(self, plugins, thresholds=None):
        self.plugins = {p.name: p for p in plugins}
        self.thresholds = thresholds or {
            "block_rate": 0.3,    # Alert if >30% requests are blocked
            "fail_rate": 0.1,     # Alert if >10% LLM-as-Judge failures
            "rate_limit_hits": 5  # Alert if >5 rate limit hits in a period
        }

    def check_metrics(self):
        """Analyzes plugin stats and prints alerts if thresholds are exceeded."""
        print("\n--- Security Monitoring Report ---")
        alerts = []

        # 1. Check Input Guardrail Block Rate
        input_guard = self.plugins.get("input_guardrail")
        if input_guard and input_guard.total_count > 0:
            block_rate = input_guard.blocked_count / input_guard.total_count
            print(f"Input Block Rate: {block_rate:.2%}")
            if block_rate > self.thresholds["block_rate"]:
                alerts.append(f"CRITICAL: High input block rate ({block_rate:.2%})!")

        # 2. Check Rate Limiter Hits
        rate_limiter = self.plugins.get("rate_limiter")
        if rate_limiter:
            print(f"Rate Limit Hits: {rate_limiter.blocked_count}")
            if rate_limiter.blocked_count > self.thresholds["rate_limit_hits"]:
                alerts.append(f"WARNING: Multiple rate limit hits detected ({rate_limiter.blocked_count})!")

        # 3. Check Output Redaction Rate
        output_guard = self.plugins.get("output_guardrail")
        if output_guard and output_guard.total_count > 0:
            redaction_rate = output_guard.redacted_count / output_guard.total_count
            print(f"Output Redaction Rate: {redaction_rate:.2%}")
            if redaction_rate > self.thresholds["block_rate"]:
                alerts.append(f"WARNING: High PII redaction rate ({redaction_rate:.2%})!")

        if not alerts:
            print("Status: All metrics within normal range.")
        else:
            print("\n!!! ALERTS TRIGGERED !!!")
            for alert in alerts:
                print(f"- {alert}")
        print("----------------------------------\n")
        return alerts
