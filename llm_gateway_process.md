# LLM Gateway Process: Portkey & Groq Fallbacks

## Overview
This document outlines how to use 3 free-tier Groq API accounts to scale inference by employing Portkey Gateway to handle load balancing, fallbacks, and error handling. 

## Justification
Groq offers lightning-fast inference on state-of-the-art open-weight models (like Llama 3). However, free tier accounts come with strict rate limits. By utilizing **Portkey** as an LLM gateway, we can combine 3 separate Groq API accounts into a single robust endpoint. 
- **Load Balancing:** Distributes requests evenly across all 3 Groq keys to avoid hitting the rate limit of a single key.
- **Fallback Logic:** If Key A hits a `429 Too Many Requests` error, Portkey instantly retries with Key B without crashing the application.
- **Zero App Code Changes:** The LangChain application still talks to the Portkey API exactly as it did before. The complex routing logic is defined in the Portkey configuration dashboard (or via JSON config headers).

## Portkey JSON Configuration Example
In your Portkey Dashboard, you can create a config like this to use 3 Groq accounts:
```json
{
  "strategy": {
    "mode": "loadbalance"
  },
  "targets": [
    {
      "provider": "groq",
      "api_key": "GROQ_KEY_1",
      "weight": 1,
      "override_params": {"model": "llama3-70b-8192"}
    },
    {
      "provider": "groq",
      "api_key": "GROQ_KEY_2",
      "weight": 1,
      "override_params": {"model": "llama3-70b-8192"}
    },
    {
      "provider": "groq",
      "api_key": "GROQ_KEY_3",
      "weight": 1,
      "override_params": {"model": "llama3-70b-8192"}
    }
  ]
}
```

---

## 10 Common Questions & Answers

1. **Why use Groq instead of OpenAI?**
   Groq runs on specialized LPU hardware making it immensely fast and completely free to use on its standard tier.

2. **Why do we need 3 Groq accounts?**
   The free tier has rate limit restrictions (e.g., Requests Per Minute). Three accounts triple our capacity when load-balanced.

3. **What is Portkey's role here?**
   Portkey acts as a router. It accepts the standard OpenAI-formatted API request and forwards it to the Groq APIs on our behalf.

4. **How does fallback work?**
   If one Groq key fails due to a rate limit or server error, Portkey intercepts the error and seamlessly routes the prompt to the next available key.

5. **Does this require changing our LangChain code?**
   No. LangChain still uses the `ChatOpenAI` client pointed at Portkey's base URL. Portkey translates the request for Groq.

6. **Will this slow down the response time?**
   Portkey adds only a negligible latency (typically <20ms), which is massively offset by Groq's high-speed inference.

7. **How do we handle models like Llama3?**
   In the Portkey configuration, we map the model name (e.g. `llama3-70b-8192`). Portkey maps the OpenAI format to Groq's format automatically.

8. **Are our prompts safe going through Portkey?**
   Yes, Portkey is SOC2 compliant and simply passes the payload through, but you can also disable data logging in their dashboard.

9. **Can we still use OpenAI as a final fallback?**
   Yes. In Portkey, you can configure a "fallback" strategy so that if all 3 Groq keys fail, it sends the request to OpenAI as a last resort.

10. **How do we monitor usage across the 3 keys?**
    Portkey's dashboard aggregates metrics (latency, cost, tokens) across all providers and keys, giving you a unified view.
