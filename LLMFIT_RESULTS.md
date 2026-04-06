
=== System Specifications ===
CPU: Apple M5 (10 cores)
Total RAM: 24.00 GB
Available RAM: 12.35 GB
Backend: Metal
GPU: Apple M5 (unified memory, 24.00 GB shared, Metal)


=== Model Compatibility Analysis ===
Found 385 compatible model(s)

╭────────────┬───────────────────────────────────────────────────────────────┬────────────────────────────────┬───────┬───────┬────────────┬──────────┬─────────┬──────┬───────┬─────────┬─────────────╮
│ Status     │ Model                                                         │ Provider                       │ Size  │ Score │ tok/s est. │ Quant    │ Runtime │ Mode │ Mem % │ Context │ Added to HF │
├────────────┼───────────────────────────────────────────────────────────────┼────────────────────────────────┼───────┼───────┼────────────┼──────────┼─────────┼──────┼───────┼─────────┼─────────────┤
│ 🟢 Perfect │ openai/gpt-oss-20b                                            │ openai                         │ 21.5B │ 93    │ 87.1       │ mlx-4bit │ MLX     │ GPU  │ 45.8% │ 131k    │ 2025-08-04  │
│ 🟢 Perfect │ RedHatAI/gpt-oss-20b                                          │ redhatai                       │ 21.5B │ 93    │ 87.1       │ mlx-4bit │ MLX     │ GPU  │ 45.8% │ 131k    │ 2025-09-04  │
│ 🟢 Perfect │ deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct                   │ DeepSeek                       │ 15.7B │ 92    │ 131.8      │ mlx-4bit │ MLX     │ GPU  │ 33.3% │ 163k    │ 2024-06-14  │
│ 🟢 Perfect │ RedHatAI/DeepSeek-Coder-V2-Lite-Instruct-FP8                  │ redhatai                       │ 15.7B │ 92    │ 144.8      │ mlx-4bit │ MLX     │ GPU  │ 33.3% │ 163k    │ 2024-07-17  │
│ 🟢 Perfect │ moonshotai/Moonlight-16B-A3B-Instruct                         │ moonshotai                     │ 16.0B │ 91    │ 202.7      │ mlx-8bit │ MLX     │ GPU  │ 34.2% │ 8k      │ 2025-02-22  │
│ 🟢 Perfect │ nvidia/Qwen3-30B-A3B-NVFP4                                    │ nvidia                         │ 15.6B │ 91    │ 137.1      │ mlx-8bit │ MLX     │ GPU  │ 33.3% │ 40k     │ 2025-07-08  │
│ 🟢 Perfect │ Qwen/Qwen1.5-MoE-A2.7B                                        │ Alibaba                        │ 14.3B │ 90    │ 144.1      │ mlx-8bit │ MLX     │ GPU  │ 30.4% │ 8k      │ 2024-02-29  │
│ 🟢 Perfect │ deepseek-ai/DeepSeek-V2-Lite-Chat                             │ DeepSeek                       │ 15.7B │ 90    │ 144.8      │ mlx-4bit │ MLX     │ GPU  │ 33.3% │ 163k    │ 2024-05-15  │
│ 🟢 Perfect │ inclusionAI/Ling-lite                                         │ inclusionai                    │ 16.8B │ 90    │ 100.0      │ mlx-8bit │ MLX     │ GPU  │ 35.8% │ 32k     │ 2025-02-28  │
│ 🟢 Perfect │ inclusionAI/LLaDA2.0-mini                                     │ inclusionai                    │ 16.3B │ 90    │ 180.5      │ mlx-8bit │ MLX     │ GPU  │ 34.6% │ 32k     │ 2025-11-25  │
│ 🟢 Perfect │ inclusionAI/LLaDA2.1-mini                                     │ inclusionai                    │ 16.3B │ 90    │ 180.5      │ mlx-8bit │ MLX     │ GPU  │ 34.6% │ 32k     │ 2026-02-09  │
│ 🟢 Perfect │ moonshotai/Moonlight-16B-A3B                                  │ moonshotai                     │ 16.0B │ 90    │ 202.7      │ mlx-8bit │ MLX     │ GPU  │ 34.2% │ 8k      │ 2025-02-22  │
│ 🟢 Perfect │ lmstudio-community/LFM2-24B-A2B-MLX-4bit                      │ lmstudio-community             │ 23.8B │ 90    │ 142.4      │ Q2_K     │ MLX     │ GPU  │ 50.8% │ 128k    │ 2026-02-23  │
│ 🟢 Perfect │ lmstudio-community/LFM2-24B-A2B-MLX-6bit                      │ lmstudio-community             │ 23.8B │ 90    │ 142.4      │ Q2_K     │ MLX     │ GPU  │ 50.8% │ 128k    │ 2026-02-23  │
│ 🟢 Perfect │ lmstudio-community/LFM2-24B-A2B-MLX-8bit                      │ lmstudio-community             │ 23.8B │ 90    │ 142.4      │ Q2_K     │ MLX     │ GPU  │ 50.8% │ 128k    │ 2026-02-23  │
│ 🟢 Perfect │ lmstudio-community/LFM2-24B-A2B-MLX-5bit                      │ lmstudio-community             │ 23.8B │ 90    │ 142.4      │ Q2_K     │ MLX     │ GPU  │ 50.8% │ 128k    │ 2026-02-23  │
│ 🟢 Perfect │ LiquidAI/LFM2-24B-A2B                                         │ Liquid AI                      │ 23.8B │ 90    │ 161.4      │ Q2_K     │ MLX     │ GPU  │ 50.8% │ 128k    │ 2026-02-24  │
│ 🟢 Perfect │ deepseek-ai/DeepSeek-V2-Lite                                  │ DeepSeek                       │ 15.7B │ 90    │ 144.8      │ mlx-4bit │ MLX     │ GPU  │ 33.3% │ 163k    │ 2024-05-15  │
│ 🟢 Perfect │ ai-sage/GigaChat3-10B-A1.8B                                   │ ai-sage                        │ 11.5B │ 88    │ 424.8      │ mlx-4bit │ MLX     │ GPU  │ 24.6% │ 262k    │ 2025-11-19  │
│ 🟢 Perfect │ deepseek-ai/DeepSeek-R1-Distill-Qwen-7B                       │ DeepSeek                       │ 7.6B  │ 87    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 67.1% │ 131k    │ 2025-01-20  │
│ 🟢 Perfect │ deepseek-ai/DeepSeek-R1-0528-Qwen3-8B                         │ DeepSeek                       │ 8.2B  │ 87    │ 28.5       │ mlx-8bit │ MLX     │ GPU  │ 72.0% │ 131k    │ 2025-05-29  │
│ 🟢 Perfect │ NVFP4/Qwen3-Coder-30B-A3B-Instruct-FP4                        │ nvfp4                          │ 15.6B │ 87    │ 217.8      │ Q2_K     │ MLX     │ GPU  │ 33.3% │ 262k    │ 2025-08-05  │
│ 🟢 Perfect │ NVFP4/Qwen3-30B-A3B-Instruct-2507-FP4                         │ nvfp4                          │ 15.6B │ 87    │ 217.8      │ Q2_K     │ MLX     │ GPU  │ 33.3% │ 262k    │ 2025-08-01  │
│ 🟢 Perfect │ microsoft/Phi-mini-MoE-instruct                               │ Microsoft                      │ 7.6B  │ 86    │ 181.1      │ mlx-8bit │ MLX     │ GPU  │ 16.2% │ 4k      │ 2025-06-23  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Coder-7B-Instruct                                │ Alibaba                        │ 7.6B  │ 86    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 42.1% │ 32k     │ 2024-09-17  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Coder-7B                                         │ Alibaba                        │ 7.6B  │ 86    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 42.1% │ 32k     │ 2024-09-16  │
│ 🟢 Perfect │ bigcode/starcoder2-7b                                         │ BigCode                        │ 7.2B  │ 86    │ 32.6       │ mlx-8bit │ MLX     │ GPU  │ 35.9% │ 16k     │ 2024-02-20  │
│ 🟢 Perfect │ LiquidAI/LFM2-8B-A1B                                          │ Liquid AI                      │ 8.3B  │ 85    │ 155.8      │ mlx-8bit │ MLX     │ GPU  │ 17.9% │ 128k    │ 2025-10-07  │
│ 🟢 Perfect │ Qwen/Qwen3-4B-Instruct-2507                                   │ Alibaba                        │ 4.0B  │ 85    │ 58.1       │ mlx-8bit │ MLX     │ GPU  │ 54.0% │ 262k    │ 2025-08-05  │
│ 🟢 Perfect │ Qwen/Qwen3-4B-Instruct-2507-FP8                               │ Alibaba                        │ 4.4B  │ 85    │ 53.0       │ mlx-8bit │ MLX     │ GPU  │ 59.0% │ 262k    │ 2025-08-06  │
│ 🟢 Perfect │ lmstudio-community/Qwen2.5-Coder-32B-Instruct-MLX-8bit        │ lmstudio-community             │ 9.2B  │ 84    │ 25.4       │ mlx-8bit │ MLX     │ GPU  │ 50.5% │ 32k     │ 2024-11-11  │
│ 🟢 Perfect │ nvidia/Qwen2.5-VL-7B-Instruct-NVFP4                           │ nvidia                         │ 5.0B  │ 84    │ 46.5       │ mlx-8bit │ MLX     │ GPU  │ 44.5% │ 128k    │ 2025-09-10  │
│ 🟢 Perfect │ microsoft/Orca-2-13b                                          │ Microsoft                      │ 13.0B │ 84    │ 18.0       │ mlx-8bit │ MLX     │ GPU  │ 58.1% │ 4k      │ —           │
│ 🟢 Perfect │ microsoft/Phi-4-multimodal-instruct                           │ Microsoft                      │ 5.6B  │ 84    │ 41.9       │ mlx-8bit │ MLX     │ GPU  │ 49.7% │ 131k    │ 2025-02-24  │
│ 🟢 Perfect │ Qwen/Qwen3-4B-Thinking-2507                                   │ Alibaba                        │ 4.0B  │ 83    │ 58.1       │ mlx-8bit │ MLX     │ GPU  │ 54.0% │ 262k    │ 2025-08-05  │
│ 🟢 Perfect │ Qwen/Qwen3.5-4B                                               │ Alibaba                        │ 4.7B  │ 83    │ 50.2       │ mlx-8bit │ MLX     │ GPU  │ 62.2% │ 262k    │ 2026-02-27  │
│ 🟢 Perfect │ Qwen/Qwen3.5-4B-Base                                          │ Alibaba                        │ 4.7B  │ 83    │ 50.2       │ mlx-8bit │ MLX     │ GPU  │ 62.2% │ 262k    │ 2026-02-27  │
│ 🟢 Perfect │ XiaomiMiMo/MiMo-7B-RL                                         │ Xiaomi                         │ 7.0B  │ 83    │ 33.4       │ mlx-8bit │ MLX     │ GPU  │ 38.9% │ 32k     │ 2025-05-01  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Coder-14B-Instruct                               │ Alibaba                        │ 14.8B │ 83    │ 15.8       │ mlx-8bit │ MLX     │ GPU  │ 79.8% │ 32k     │ 2024-11-06  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Coder-14B                                        │ Alibaba                        │ 14.8B │ 83    │ 15.8       │ mlx-8bit │ MLX     │ GPU  │ 79.8% │ 32k     │ 2024-11-08  │
│ 🟢 Perfect │ Qwen/Qwen2.5-VL-3B-Instruct                                   │ Alibaba                        │ 3.8B  │ 83    │ 62.3       │ mlx-8bit │ MLX     │ GPU  │ 33.7% │ 128k    │ 2025-01-26  │
│ 🟢 Perfect │ nvidia/Nemotron-H-4B-Instruct-128K                            │ nvidia                         │ 4.5B  │ 83    │ 52.1       │ mlx-8bit │ MLX     │ GPU  │ 40.4% │ 131k    │ 2025-04-15  │
│ 🟢 Perfect │ allenai/Olmo-3-7B-Instruct-SFT                                │ allenai                        │ 7.3B  │ 83    │ 32.0       │ mlx-8bit │ MLX     │ GPU  │ 48.4% │ 65k     │ 2025-11-17  │
│ 🟢 Perfect │ RedHatAI/Llama-3.2-3B-Instruct-FP8                            │ redhatai                       │ 3.6B  │ 83    │ 64.8       │ mlx-8bit │ MLX     │ GPU  │ 32.9% │ 131k    │ 2024-09-26  │
│ 🟢 Perfect │ Qwen/Qwen2.5-7B                                               │ Alibaba                        │ 7.6B  │ 83    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 67.1% │ 131k    │ 2024-09-15  │
│ 🟢 Perfect │ Qwen/Qwen2-7B                                                 │ Alibaba                        │ 7.6B  │ 83    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 67.1% │ 131k    │ 2024-06-04  │
│ 🟢 Perfect │ allenai/Olmo-3-1025-7B                                        │ allenai                        │ 7.3B  │ 83    │ 32.0       │ mlx-8bit │ MLX     │ GPU  │ 48.4% │ 65k     │ 2025-09-12  │
│ 🟢 Perfect │ google/gemma-3n-E4B-it                                        │ Google                         │ 8B    │ 83    │ 29.2       │ mlx-8bit │ MLX     │ GPU  │ 70.4% │ 131k    │ 2025-06-25  │
│ 🟢 Perfect │ mistralai/Mistral-7B-Instruct-v0.2                            │ Mistral AI                     │ 7.2B  │ 82    │ 32.3       │ mlx-8bit │ MLX     │ GPU  │ 40.2% │ 32k     │ 2023-12-11  │
│ 🟢 Perfect │ mistralai/Mistral-7B-Instruct-v0.3                            │ Mistral AI                     │ 7.2B  │ 82    │ 32.3       │ mlx-8bit │ MLX     │ GPU  │ 40.2% │ 32k     │ 2024-05-22  │
│ 🟢 Perfect │ openchat/openchat-3.5-0106                                    │ OpenChat                       │ 7.0B  │ 82    │ 33.4       │ mlx-8bit │ MLX     │ GPU  │ 33.2% │ 8k      │ —           │
│ 🟢 Perfect │ mistralai/Mistral-7B-v0.1                                     │ Mistral AI                     │ 7.2B  │ 82    │ 32.3       │ mlx-8bit │ MLX     │ GPU  │ 40.2% │ 32k     │ 2023-09-20  │
│ 🟢 Perfect │ dphn/dolphin-2.6-mistral-7b                                   │ dphn                           │ 7.2B  │ 82    │ 32.3       │ mlx-8bit │ MLX     │ GPU  │ 40.2% │ 32k     │ 2023-12-27  │
│ 🟢 Perfect │ Nanbeige/Nanbeige4.1-3B                                       │ nanbeige                       │ 3.9B  │ 82    │ 59.4       │ mlx-8bit │ MLX     │ GPU  │ 52.8% │ 262k    │ 2026-02-10  │
│ 🟢 Perfect │ janhq/Jan-v1-4B                                               │ janhq                          │ 4.0B  │ 82    │ 58.1       │ mlx-8bit │ MLX     │ GPU  │ 54.0% │ 262k    │ 2025-08-08  │
│ 🟢 Perfect │ Dream-org/Dream-v0-Instruct-7B                                │ dream-org                      │ 7.6B  │ 82    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 67.1% │ 131k    │ 2025-04-03  │
│ 🟢 Perfect │ bigcode/starcoder2-15b                                        │ BigCode                        │ 15.7B │ 82    │ 14.9       │ mlx-8bit │ MLX     │ GPU  │ 76.1% │ 16k     │ —           │
│ 🟢 Perfect │ HuggingFaceH4/zephyr-7b-beta                                  │ HuggingFace                    │ 7.2B  │ 82    │ 32.3       │ mlx-8bit │ MLX     │ GPU  │ 40.2% │ 32k     │ 2023-10-26  │
│ 🟢 Perfect │ prometheus-eval/prometheus-7b-v2.0                            │ prometheus-eval                │ 7.2B  │ 82    │ 32.3       │ mlx-8bit │ MLX     │ GPU  │ 40.2% │ 32k     │ 2024-02-13  │
│ 🟢 Perfect │ Salesforce/xLAM-7b-r                                          │ salesforce                     │ 7.2B  │ 82    │ 32.3       │ mlx-8bit │ MLX     │ GPU  │ 40.2% │ 32k     │ 2024-08-28  │
│ 🟢 Perfect │ Qwen/Qwen2.5-7B-Instruct                                      │ Alibaba                        │ 7.6B  │ 82    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 42.1% │ 32k     │ 2024-09-16  │
│ 🟢 Perfect │ Qwen/Qwen2-7B-Instruct                                        │ Alibaba                        │ 7.6B  │ 82    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 42.1% │ 32k     │ 2024-06-04  │
│ 🟢 Perfect │ lmstudio-community/Qwen2.5-Coder-32B-Instruct-MLX-4bit        │ lmstudio-community             │ 5.1B  │ 82    │ 45.7       │ mlx-8bit │ MLX     │ GPU  │ 29.0% │ 32k     │ 2024-11-11  │
│ 🟢 Perfect │ lmstudio-community/QwQ-32B-MLX-4bit                           │ lmstudio-community             │ 5.1B  │ 82    │ 45.7       │ mlx-8bit │ MLX     │ GPU  │ 45.8% │ 131k    │ 2025-03-05  │
│ 🟢 Perfect │ omni-research/Tarsier-7b                                      │ omni-research                  │ 7.1B  │ 82    │ 33.1       │ mlx-8bit │ MLX     │ GPU  │ 32.5% │ 4k      │ 2024-07-04  │
│ 🟢 Perfect │ Qwen/Qwen-7B                                                  │ Alibaba                        │ 7.7B  │ 82    │ 30.3       │ mlx-8bit │ MLX     │ GPU  │ 42.7% │ 32k     │ 2023-08-03  │
│ 🟢 Perfect │ Qwen/Qwen1.5-7B                                               │ Alibaba                        │ 7.7B  │ 82    │ 30.3       │ mlx-8bit │ MLX     │ GPU  │ 42.7% │ 32k     │ 2024-01-22  │
│ 🟢 Perfect │ NousResearch/Hermes-3-Llama-3.1-8B                            │ NousResearch                   │ 8.0B  │ 82    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 70.6% │ 131k    │ 2024-07-28  │
│ 🟢 Perfect │ nvidia/Llama-3.1-Nemotron-Nano-8B-v1                          │ nvidia                         │ 8.0B  │ 82    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 70.6% │ 131k    │ 2025-03-16  │
│ 🟢 Perfect │ RedHatAI/Meta-Llama-3.1-8B-FP8                                │ redhatai                       │ 8.0B  │ 82    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 70.6% │ 131k    │ 2024-07-31  │
│ 🟢 Perfect │ WizardLMTeam/WizardCoder-15B-V1.0                             │ WizardLM                       │ 15.5B │ 82    │ 15.1       │ mlx-8bit │ MLX     │ GPU  │ 71.0% │ 8k      │ —           │
│ 🟢 Perfect │ tiiuae/Falcon3-7B-Instruct                                    │ TII                            │ 7.5B  │ 81    │ 31.4       │ mlx-8bit │ MLX     │ GPU  │ 41.3% │ 32k     │ 2024-11-29  │
│ 🟢 Perfect │ Qwen/Qwen-7B-Chat                                             │ Alibaba                        │ 7.7B  │ 81    │ 30.3       │ mlx-8bit │ MLX     │ GPU  │ 42.7% │ 32k     │ 2023-08-03  │
│ 🟢 Perfect │ tiiuae/falcon-7b-instruct                                     │ TII                            │ 7.2B  │ 81    │ 32.4       │ mlx-8bit │ MLX     │ GPU  │ 33.1% │ 4k      │ 2023-04-25  │
│ 🟢 Perfect │ NousResearch/Meta-Llama-3.1-8B-Instruct                       │ NousResearch                   │ 8.0B  │ 81    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 70.6% │ 131k    │ 2024-07-24  │
│ 🟢 Perfect │ nvidia/Llama-3.1-8B-Instruct-FP8                              │ nvidia                         │ 8.0B  │ 81    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 70.6% │ 131k    │ 2024-08-29  │
│ 🟢 Perfect │ PatronusAI/Llama-3-Patronus-Lynx-8B-Instruct-v1.1             │ patronusai                     │ 8.0B  │ 81    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 70.6% │ 131k    │ 2024-07-24  │
│ 🟢 Perfect │ RedHatAI/Meta-Llama-3.1-8B-Instruct-FP8                       │ redhatai                       │ 8.0B  │ 81    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 70.6% │ 131k    │ 2024-07-23  │
│ 🟢 Perfect │ RedHatAI/Meta-Llama-3.1-8B-Instruct-FP8-dynamic               │ redhatai                       │ 8.0B  │ 81    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 70.6% │ 131k    │ 2024-07-23  │
│ 🟢 Perfect │ google/gemma-3-12b-it                                         │ Google                         │ 12B   │ 81    │ 26.4       │ mlx-4bit │ MLX     │ GPU  │ 82.0% │ 131k    │ —           │
│ 🟢 Perfect │ tiiuae/falcon-mamba-7b-instruct                               │ TII                            │ 7.3B  │ 81    │ 32.1       │ mlx-8bit │ MLX     │ GPU  │ 33.4% │ 4k      │ 2024-07-30  │
│ 🟢 Perfect │ Qwen/Qwen2.5-3B-Instruct                                      │ Alibaba                        │ 3.1B  │ 81    │ 75.7       │ mlx-8bit │ MLX     │ GPU  │ 18.3% │ 32k     │ 2024-09-17  │
│ 🟢 Perfect │ tiiuae/falcon-7b                                              │ TII                            │ 7.2B  │ 81    │ 32.4       │ mlx-8bit │ MLX     │ GPU  │ 33.1% │ 4k      │ 2023-04-24  │
│ 🟢 Perfect │ lmstudio-community/Qwen2.5-Coder-14B-Instruct-MLX-8bit        │ lmstudio-community             │ 4.2B  │ 81    │ 56.3       │ mlx-8bit │ MLX     │ GPU  │ 23.9% │ 32k     │ 2024-11-11  │
│ 🟢 Perfect │ RedHatAI/Qwen3-32B-quantized.w4a16                            │ redhatai                       │ 5.7B  │ 81    │ 41.0       │ mlx-8bit │ MLX     │ GPU  │ 33.6% │ 40k     │ 2025-05-05  │
│ 🟢 Perfect │ allenai/wildguard                                             │ allenai                        │ 7.2B  │ 81    │ 32.3       │ mlx-8bit │ MLX     │ GPU  │ 33.3% │ 4k      │ 2024-06-15  │
│ 🟢 Perfect │ XCurOS/XCurOS-0.1-8B-Instruct                                 │ xcuros                         │ 7.6B  │ 81    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 42.1% │ 32k     │ 2026-02-28  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Math-7B                                          │ Alibaba                        │ 7.6B  │ 81    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 34.9% │ 4k      │ 2024-09-16  │
│ 🟢 Perfect │ deepseek-ai/DeepSeek-R1-Distill-Qwen-14B                      │ DeepSeek                       │ 14.8B │ 81    │ 15.8       │ mlx-8bit │ MLX     │ GPU  │ 95.9% │ 131k    │ 2025-01-20  │
│ 🟢 Perfect │ SWE-bench/SWE-agent-LM-7B                                     │ swe-bench                      │ 7.6B  │ 81    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 42.1% │ 32k     │ 2025-07-12  │
│ 🟢 Perfect │ UCSB-SURFI/VulnLLM-R-7B                                       │ ucsb-surfi                     │ 7.6B  │ 81    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 42.1% │ 32k     │ 2025-06-05  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Math-7B-Instruct                                 │ Alibaba                        │ 7.6B  │ 81    │ 30.7       │ mlx-8bit │ MLX     │ GPU  │ 34.9% │ 4k      │ 2024-09-19  │
│ 🟢 Perfect │ lmms-lab/llava-onevision-qwen2-7b-ov                          │ lmms-lab                       │ 8.0B  │ 81    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 44.3% │ 32k     │ 2024-06-29  │
│ 🟢 Perfect │ nvidia/Qwen3-14B-NVFP4                                        │ nvidia                         │ 8.2B  │ 81    │ 28.6       │ mlx-8bit │ MLX     │ GPU  │ 47.2% │ 40k     │ 2025-09-09  │
│ 🟢 Perfect │ meta-llama/Llama-3.2-3B-Instruct                              │ Meta                           │ 3.2B  │ 81    │ 72.8       │ mlx-8bit │ MLX     │ GPU  │ 15.9% │ 4k      │ 2024-09-18  │
│ 🟢 Perfect │ Qwen/Qwen3-8B                                                 │ Alibaba                        │ 8.2B  │ 81    │ 28.5       │ mlx-8bit │ MLX     │ GPU  │ 47.4% │ 40k     │ 2025-04-27  │
│ 🟢 Perfect │ Qwen/Qwen3-8B-FP8                                             │ Alibaba                        │ 8.2B  │ 81    │ 28.5       │ mlx-8bit │ MLX     │ GPU  │ 47.4% │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ nytopop/Qwen3-8B.w8a8                                         │ nytopop                        │ 8.2B  │ 81    │ 28.5       │ mlx-8bit │ MLX     │ GPU  │ 47.4% │ 40k     │ 2025-04-29  │
│ 🟢 Perfect │ RedHatAI/Qwen3-8B-FP8-dynamic                                 │ redhatai                       │ 8.2B  │ 81    │ 28.5       │ mlx-8bit │ MLX     │ GPU  │ 47.4% │ 40k     │ 2025-05-02  │
│ 🟢 Perfect │ TIGER-Lab/VLM2Vec-Full                                        │ tiger-lab                      │ 4.1B  │ 80    │ 56.4       │ mlx-8bit │ MLX     │ GPU  │ 37.5% │ 131k    │ 2024-10-08  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-32B-MLX-4bit                         │ lmstudio-community             │ 5.1B  │ 80    │ 45.7       │ mlx-8bit │ MLX     │ GPU  │ 30.4% │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ Qwen/Qwen3-8B-Base                                            │ Alibaba                        │ 8.2B  │ 80    │ 28.5       │ mlx-8bit │ MLX     │ GPU  │ 45.2% │ 32k     │ 2025-04-28  │
│ 🟢 Perfect │ Qwen/Qwen2.5-VL-7B-Instruct                                   │ Alibaba                        │ 8.3B  │ 80    │ 28.2       │ mlx-8bit │ MLX     │ GPU  │ 72.0% │ 128k    │ 2025-01-26  │
│ 🟢 Perfect │ NousResearch/Hermes-3-Llama-3.2-3B                            │ NousResearch                   │ 3.2B  │ 80    │ 72.8       │ mlx-8bit │ MLX     │ GPU  │ 29.5% │ 131k    │ 2024-12-03  │
│ 🟢 Perfect │ Menlo/Jan-nano-128k                                           │ menlo                          │ 4.0B  │ 80    │ 58.1       │ mlx-8bit │ MLX     │ GPU  │ 36.4% │ 131k    │ 2025-06-25  │
│ 🟢 Perfect │ LGAI-EXAONE/EXAONE-Deep-7.8B                                  │ lgai-exaone                    │ 7.8B  │ 80    │ 29.9       │ mlx-8bit │ MLX     │ GPU  │ 43.2% │ 32k     │ 2025-03-12  │
│ 🟢 Perfect │ nvidia/Qwen3-8B-NVFP4                                         │ nvidia                         │ 4.7B  │ 80    │ 49.5       │ mlx-8bit │ MLX     │ GPU  │ 28.2% │ 40k     │ 2025-09-09  │
│ 🟢 Perfect │ XiaomiMiMo/MiMo-7B-Base                                       │ xiaomimimo                     │ 7.8B  │ 80    │ 29.8       │ mlx-8bit │ MLX     │ GPU  │ 43.3% │ 32k     │ 2025-04-29  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Coder-3B-Instruct                                │ Alibaba                        │ 3.1B  │ 80    │ 75.7       │ mlx-8bit │ MLX     │ GPU  │ 18.3% │ 32k     │ 2024-11-06  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Coder-3B                                         │ Alibaba                        │ 3.1B  │ 80    │ 75.7       │ mlx-8bit │ MLX     │ GPU  │ 18.3% │ 32k     │ 2024-11-08  │
│ 🟢 Perfect │ microsoft/Phi-3.5-mini-instruct                               │ Microsoft                      │ 3.8B  │ 80    │ 61.2       │ mlx-8bit │ MLX     │ GPU  │ 34.7% │ 131k    │ —           │
│ 🟢 Perfect │ zstanjj/HTML-Pruner-Phi-3.8B                                  │ zstanjj                        │ 3.8B  │ 80    │ 61.2       │ mlx-8bit │ MLX     │ GPU  │ 34.7% │ 131k    │ 2024-10-16  │
│ 🟢 Perfect │ mistralai/Ministral-8B-Instruct-2410                          │ Mistral AI                     │ 8.0B  │ 80    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 44.3% │ 32k     │ —           │
│ 🟢 Perfect │ Qwen/Qwen3-4B-SafeRL                                          │ Alibaba                        │ 4.4B  │ 80    │ 53.0       │ mlx-8bit │ MLX     │ GPU  │ 26.5% │ 40k     │ 2025-09-30  │
│ 🟢 Perfect │ Qwen/Qwen3-4B-FP8                                             │ Alibaba                        │ 4.4B  │ 80    │ 53.0       │ mlx-8bit │ MLX     │ GPU  │ 26.5% │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ 01-ai/Yi-6B-Chat                                              │ 01.ai                          │ 6.1B  │ 80    │ 38.6       │ mlx-8bit │ MLX     │ GPU  │ 28.2% │ 4k      │ 2023-11-22  │
│ 🟢 Perfect │ IlyaGusev/saiga_llama3_8b                                     │ ilyagusev                      │ 8.0B  │ 80    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 37.7% │ 8k      │ 2024-04-18  │
│ 🟢 Perfect │ ibm-granite/granite-3.3-8b-instruct                           │ ibm-granite                    │ 8.2B  │ 80    │ 28.6       │ mlx-8bit │ MLX     │ GPU  │ 71.8% │ 131k    │ 2025-04-09  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-14B-MLX-8bit                         │ lmstudio-community             │ 4.2B  │ 80    │ 56.3       │ mlx-8bit │ MLX     │ GPU  │ 25.1% │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ deepseek-ai/deepseek-coder-6.7b-instruct                      │ DeepSeek                       │ 6.7B  │ 80    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 33.9% │ 16k     │ 2023-10-29  │
│ 🟢 Perfect │ deepseek-ai/deepseek-coder-6.7b-base                          │ DeepSeek                       │ 6.7B  │ 80    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 33.9% │ 16k     │ 2023-10-23  │
│ 🟢 Perfect │ meta-llama/Llama-3.1-8B                                       │ Meta                           │ 8.0B  │ 80    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 36.6% │ 4k      │ 2024-07-14  │
│ 🟢 Perfect │ meta-llama/Meta-Llama-3-8B                                    │ Meta                           │ 8.0B  │ 80    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 36.6% │ 4k      │ 2024-04-17  │
│ 🟢 Perfect │ meta-llama/Llama-Guard-3-8B                                   │ Meta                           │ 8.0B  │ 80    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 36.6% │ 4k      │ 2024-07-22  │
│ 🟢 Perfect │ hirundo-io/llama-3.1-8b-bias-reduced                          │ hirundo-io                     │ 8.0B  │ 80    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 36.6% │ 4k      │ 2025-10-22  │
│ 🟢 Perfect │ allenai/OLMoE-1B-7B-0125-Instruct                             │ allenai                        │ 6.9B  │ 80    │ 200.2      │ mlx-8bit │ MLX     │ GPU  │ 14.6% │ 4k      │ 2025-01-27  │
│ 🟢 Perfect │ Qwen/Qwen3-4B-Base                                            │ Alibaba                        │ 4.0B  │ 80    │ 58.1       │ mlx-8bit │ MLX     │ GPU  │ 23.2% │ 32k     │ 2025-04-28  │
│ 🟢 Perfect │ BSC-LT/salamandra-7b-instruct                                 │ bsc-lt                         │ 7.8B  │ 80    │ 30.1       │ mlx-8bit │ MLX     │ GPU  │ 36.6% │ 8k      │ 2024-09-30  │
│ 🟢 Perfect │ meta-llama/Llama-3.1-8B-Instruct                              │ Meta                           │ 8.0B  │ 80    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 36.6% │ 4k      │ 2024-07-18  │
│ 🟢 Perfect │ meta-llama/Meta-Llama-3-8B-Instruct                           │ Meta                           │ 8.0B  │ 80    │ 29.1       │ mlx-8bit │ MLX     │ GPU  │ 36.6% │ 4k      │ 2024-04-17  │
│ 🟢 Perfect │ microsoft/Orca-2-7b                                           │ Microsoft                      │ 7.0B  │ 80    │ 33.3       │ mlx-8bit │ MLX     │ GPU  │ 32.3% │ 4k      │ —           │
│ 🟢 Perfect │ bigcode/starcoder2-3b                                         │ BigCode                        │ 3.0B  │ 80    │ 77.1       │ mlx-8bit │ MLX     │ GPU  │ 16.4% │ 16k     │ 2023-11-29  │
│ 🟢 Perfect │ ibm-granite/granite-4.0-h-micro                               │ ibm-granite                    │ 3.2B  │ 80    │ 73.2       │ mlx-8bit │ MLX     │ GPU  │ 29.3% │ 131k    │ 2025-09-16  │
│ 🟢 Perfect │ meta-llama/CodeLlama-13b-Instruct-hf                          │ Meta                           │ 13.0B │ 80    │ 18.0       │ mlx-8bit │ MLX     │ GPU  │ 58.1% │ 4k      │ 2024-03-13  │
│ 🟢 Perfect │ codellama/CodeLlama-7b-Instruct-hf                            │ codellama                      │ 6.7B  │ 79    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 33.8% │ 16k     │ 2023-08-24  │
│ 🟢 Perfect │ codellama/CodeLlama-7b-hf                                     │ codellama                      │ 6.7B  │ 79    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 33.8% │ 16k     │ 2023-08-24  │
│ 🟢 Perfect │ JetLM/SDAR-8B-Chat-b32                                        │ jetlm                          │ 8.2B  │ 79    │ 28.5       │ mlx-8bit │ MLX     │ GPU  │ 45.2% │ 32k     │ 2025-09-09  │
│ 🟢 Perfect │ microsoft/phi-4                                               │ Microsoft                      │ 14B   │ 79    │ 16.7       │ mlx-8bit │ MLX     │ GPU  │ 68.1% │ 16k     │ —           │
│ 🟢 Perfect │ microsoft/Phi-4-reasoning                                     │ Microsoft                      │ 14B   │ 79    │ 16.7       │ mlx-8bit │ MLX     │ GPU  │ 75.7% │ 32k     │ 2025-04-01  │
│ 🟢 Perfect │ Qwen/Qwen2.5-3B                                               │ Alibaba                        │ 3.1B  │ 79    │ 75.7       │ mlx-8bit │ MLX     │ GPU  │ 18.3% │ 32k     │ 2024-09-15  │
│ 🟢 Perfect │ EssentialAI/rnj-1-instruct                                    │ essentialai                    │ 8.3B  │ 79    │ 28.1       │ mlx-8bit │ MLX     │ GPU  │ 45.8% │ 32k     │ 2025-12-04  │
│ 🟢 Perfect │ microsoft/Phi-tiny-MoE-instruct                               │ Microsoft                      │ 3.8B  │ 79    │ 368.9      │ mlx-8bit │ MLX     │ GPU  │ 7.9%  │ 4k      │ 2025-06-23  │
│ 🟢 Perfect │ meta-llama/Llama-3.2-3B                                       │ Meta                           │ 3.2B  │ 79    │ 72.8       │ mlx-8bit │ MLX     │ GPU  │ 15.9% │ 4k      │ 2024-09-18  │
│ 🟢 Perfect │ google/gemma-3n-E2B-it                                        │ Google                         │ 4B    │ 79    │ 58.4       │ mlx-8bit │ MLX     │ GPU  │ 36.2% │ 131k    │ 2025-06-25  │
│ 🟢 Perfect │ HuggingFaceTB/SmolLM3-3B                                      │ huggingfacetb                  │ 3.1B  │ 79    │ 76.0       │ mlx-8bit │ MLX     │ GPU  │ 21.6% │ 65k     │ 2025-07-08  │
│ 🟢 Perfect │ HuggingFaceTB/SmolLM3-3B-Base                                 │ huggingfacetb                  │ 3.1B  │ 79    │ 76.0       │ mlx-8bit │ MLX     │ GPU  │ 21.6% │ 65k     │ 2025-06-19  │
│ 🟢 Perfect │ nvidia/Nemotron-H-4B-Base-8K                                  │ nvidia                         │ 4.5B  │ 79    │ 52.1       │ mlx-8bit │ MLX     │ GPU  │ 22.0% │ 8k      │ 2025-03-20  │
│ 🟢 Perfect │ nvidia/NVIDIA-Nemotron-Nano-9B-v2                             │ nvidia                         │ 8.9B  │ 78    │ 26.3       │ mlx-8bit │ MLX     │ GPU  │ 78.0% │ 131k    │ 2025-08-12  │
│ 🟢 Perfect │ nvidia/NVIDIA-Nemotron-Nano-9B-v2-Japanese                    │ nvidia                         │ 8.9B  │ 78    │ 26.3       │ mlx-8bit │ MLX     │ GPU  │ 78.0% │ 131k    │ 2026-02-04  │
│ 🟢 Perfect │ nvidia/NVIDIA-Nemotron-Nano-9B-v2-Base                        │ nvidia                         │ 8.9B  │ 78    │ 26.3       │ mlx-8bit │ MLX     │ GPU  │ 78.0% │ 131k    │ 2025-08-14  │
│ 🟢 Perfect │ nvidia/NVIDIA-Nemotron-Nano-9B-v2-FP8                         │ nvidia                         │ 8.9B  │ 78    │ 26.3       │ mlx-8bit │ MLX     │ GPU  │ 78.0% │ 131k    │ 2025-09-22  │
│ 🟢 Perfect │ nvidia/Mistral-NeMo-Minitron-8B-Instruct                      │ nvidia                         │ 8.4B  │ 78    │ 27.8       │ mlx-8bit │ MLX     │ GPU  │ 39.4% │ 8k      │ 2024-10-02  │
│ 🟢 Perfect │ Salesforce/xLAM-2-3b-fc-r                                     │ salesforce                     │ 3.1B  │ 78    │ 75.7       │ mlx-8bit │ MLX     │ GPU  │ 18.3% │ 32k     │ 2025-03-27  │
│ 🟢 Perfect │ microsoft/phi-3-mini-4k-instruct                              │ Microsoft                      │ 3.8B  │ 78    │ 61.2       │ mlx-8bit │ MLX     │ GPU  │ 18.5% │ 4k      │ —           │
│ 🟢 Perfect │ naver-hyperclovax/HyperCLOVAX-SEED-Omni-8B                    │ naver-hyperclovax              │ 10.7B │ 78    │ 21.8       │ mlx-8bit │ MLX     │ GPU  │ 49.8% │ 8k      │ 2025-12-23  │
│ 🟢 Perfect │ ibm-research/PowerLM-3b                                       │ ibm-research                   │ 3.5B  │ 78    │ 66.6       │ mlx-8bit │ MLX     │ GPU  │ 17.2% │ 4k      │ 2024-08-14  │
│ 🟢 Perfect │ NousResearch/Llama-2-7b-chat-hf                               │ NousResearch                   │ 6.7B  │ 78    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 31.1% │ 4k      │ 2023-07-18  │
│ 🟢 Perfect │ allenai/OLMoE-1B-7B-0125                                      │ allenai                        │ 6.9B  │ 78    │ 200.2      │ mlx-8bit │ MLX     │ GPU  │ 14.6% │ 4k      │ 2025-01-21  │
│ 🟢 Perfect │ ibm-granite/granite-4.0-h-tiny                                │ ibm-granite                    │ 6.9B  │ 78    │ 242.2      │ mlx-8bit │ MLX     │ GPU  │ 15.0% │ 131k    │ 2025-09-16  │
│ 🟢 Perfect │ meta-llama/Llama-3.2-11B-Vision-Instruct                      │ Meta                           │ 10.7B │ 78    │ 21.9       │ mlx-8bit │ MLX     │ GPU  │ 48.0% │ 4k      │ 2024-09-18  │
│ 🟢 Perfect │ google/gemma-2-9b-it                                          │ Google                         │ 9.2B  │ 77    │ 25.3       │ mlx-8bit │ MLX     │ GPU  │ 41.9% │ 4k      │ 2024-06-24  │
│ 🟢 Perfect │ lmsys/vicuna-7b-v1.5                                          │ LMSYS                          │ 7.0B  │ 77    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 31.1% │ 4k      │ —           │
│ 🟢 Perfect │ ibm-research/PowerMoE-3b                                      │ ibm-research                   │ 3.4B  │ 77    │ 288.6      │ mlx-8bit │ MLX     │ GPU  │ 7.1%  │ 4k      │ 2024-08-14  │
│ 🟢 Perfect │ zai-org/glm-4-9b                                              │ zai-org                        │ 9.4B  │ 77    │ 24.9       │ mlx-8bit │ MLX     │ GPU  │ 43.8% │ 8k      │ 2024-06-04  │
│ 🟢 Perfect │ upstage/SOLAR-10.7B-Instruct-v1.0                             │ Upstage                        │ 10.7B │ 77    │ 21.8       │ mlx-8bit │ MLX     │ GPU  │ 48.3% │ 4k      │ 2023-12-12  │
│ 🟢 Perfect │ NousResearch/Nous-Hermes-llama-2-7b                           │ NousResearch                   │ 6.7B  │ 77    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 31.1% │ 4k      │ 2023-07-25  │
│ 🟢 Perfect │ meta-llama/Llama-2-7b-hf                                      │ Meta                           │ 6.7B  │ 77    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 31.1% │ 4k      │ 2023-07-13  │
│ 🟢 Perfect │ NousResearch/Llama-2-7b-hf                                    │ NousResearch                   │ 6.7B  │ 77    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 31.1% │ 4k      │ 2023-07-18  │
│ 🟢 Perfect │ kmhf/hf-moshiko                                               │ kmhf                           │ 7.8B  │ 76    │ 30.0       │ mlx-8bit │ MLX     │ GPU  │ 35.3% │ 3k      │ 2024-09-27  │
│ 🟢 Perfect │ speakleash/Bielik-11B-v3.0-Instruct                           │ speakleash                     │ 11.2B │ 76    │ 20.9       │ mlx-8bit │ MLX     │ GPU  │ 50.1% │ 4k      │ 2025-11-07  │
│ 🟢 Perfect │ tartuNLP/Llammas-base-p1-GPT-4o-human-error-mix-paragraph-GEC │ tartunlp                       │ 6.7B  │ 76    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 31.1% │ 4k      │ 2025-02-11  │
│ 🟢 Perfect │ XLabs-AI/xflux_text_encoders                                  │ xlabs-ai                       │ 4.8B  │ 75    │ 49.1       │ mlx-8bit │ MLX     │ GPU  │ 22.6% │ 4k      │ 2024-08-11  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-4B-Instruct-2507-MLX-8bit            │ lmstudio-community             │ 1.1B  │ 75    │ 206.6      │ mlx-8bit │ MLX     │ GPU  │ 16.7% │ 262k    │ 2025-08-06  │
│ 🟢 Perfect │ mistralai/Mistral-Nemo-Instruct-2407                          │ Mistral AI                     │ 12.2B │ 75    │ 25.8       │ mlx-4bit │ MLX     │ GPU  │ 83.7% │ 131k    │ —           │
│ 🟢 Perfect │ llm-jp/llm-jp-3.1-13b                                         │ llm-jp                         │ 13.7B │ 75    │ 17.1       │ mlx-8bit │ MLX     │ GPU  │ 61.1% │ 4k      │ 2025-05-23  │
│ 🟢 Perfect │ Qwen/Qwen3-14B-Base                                           │ Alibaba                        │ 14.8B │ 75    │ 15.8       │ mlx-8bit │ MLX     │ GPU  │ 79.7% │ 32k     │ 2025-04-28  │
│ 🟢 Perfect │ RedHatAI/Llama-3.2-1B-Instruct-FP8                            │ redhatai                       │ 1.5B  │ 75    │ 156.0      │ mlx-8bit │ MLX     │ GPU  │ 14.9% │ 131k    │ 2024-09-26  │
│ 🟢 Perfect │ RedHatAI/Llama-3.2-1B-Instruct-FP8-dynamic                    │ redhatai                       │ 1.5B  │ 75    │ 156.0      │ mlx-8bit │ MLX     │ GPU  │ 14.9% │ 131k    │ 2024-09-25  │
│ 🟢 Perfect │ meta-llama/CodeLlama-7b-Instruct-hf                           │ Meta                           │ 6.7B  │ 75    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 31.1% │ 4k      │ 2024-03-13  │
│ 🟢 Perfect │ microsoft/Phi-4-mini-reasoning                                │ Microsoft                      │ 3.8B  │ 74    │ 61.5       │ mlx-8bit │ MLX     │ GPU  │ 20.0% │ 16k     │ 2025-04-01  │
│ 🟢 Perfect │ microsoft/Phi-3-medium-14b-instruct                           │ Microsoft                      │ 14B   │ 74    │ 16.7       │ mlx-8bit │ MLX     │ GPU  │ 62.3% │ 4k      │ —           │
│ 🟢 Perfect │ Vikhrmodels/Vikhr-Llama-3.2-1B-Instruct                       │ vikhrmodels                    │ 1.2B  │ 74    │ 189.1      │ mlx-8bit │ MLX     │ GPU  │ 12.6% │ 131k    │ 2024-09-27  │
│ 🟢 Perfect │ Qwen/Qwen1.5-1.8B-Chat                                        │ Alibaba                        │ 1.8B  │ 74    │ 127.3      │ mlx-8bit │ MLX     │ GPU  │ 11.7% │ 32k     │ 2024-01-30  │
│ 🟢 Perfect │ Qwen/Qwen2.5-1.5B-Instruct                                    │ Alibaba                        │ 1.5B  │ 74    │ 151.4      │ mlx-8bit │ MLX     │ GPU  │ 10.2% │ 32k     │ 2024-09-17  │
│ 🟢 Perfect │ Qwen/Qwen2-1.5B-Instruct                                      │ Alibaba                        │ 1.5B  │ 74    │ 151.4      │ mlx-8bit │ MLX     │ GPU  │ 10.2% │ 32k     │ 2024-06-03  │
│ 🟢 Perfect │ RedHatAI/Qwen2-1.5B-Instruct-FP8                              │ redhatai                       │ 1.5B  │ 74    │ 151.4      │ mlx-8bit │ MLX     │ GPU  │ 10.2% │ 32k     │ 2024-06-14  │
│ 🟢 Perfect │ deepseek-ai/deepseek-moe-16b-base                             │ DeepSeek                       │ 16.4B │ 74    │ 14.3       │ mlx-8bit │ MLX     │ GPU  │ 72.6% │ 4k      │ 2024-01-08  │
│ 🟢 Perfect │ Qwen/Qwen3.5-2B                                               │ Alibaba                        │ 2.3B  │ 74    │ 102.8      │ mlx-8bit │ MLX     │ GPU  │ 31.4% │ 262k    │ 2026-02-28  │
│ 🟢 Perfect │ Qwen/Qwen3.5-2B-Base                                          │ Alibaba                        │ 2.3B  │ 74    │ 102.8      │ mlx-8bit │ MLX     │ GPU  │ 31.4% │ 262k    │ 2026-02-28  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Math-1.5B-Instruct                               │ Alibaba                        │ 1.5B  │ 74    │ 151.4      │ mlx-8bit │ MLX     │ GPU  │ 8.7%  │ 4k      │ 2024-09-16  │
│ 🟢 Perfect │ LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct                          │ lgai-exaone                    │ 2.4B  │ 74    │ 97.2       │ mlx-8bit │ MLX     │ GPU  │ 14.7% │ 32k     │ 2024-12-01  │
│ 🟢 Perfect │ meta-llama/Llama-3.2-1B-Instruct                              │ Meta                           │ 1.2B  │ 74    │ 189.1      │ mlx-8bit │ MLX     │ GPU  │ 7.4%  │ 4k      │ 2024-09-18  │
│ 🟢 Perfect │ cazzz307/Abliterated-Llama-3.2-1B-Instruct                    │ cazzz307                       │ 1.2B  │ 74    │ 189.1      │ mlx-8bit │ MLX     │ GPU  │ 7.4%  │ 4k      │ 2025-12-04  │
│ 🟢 Perfect │ huggyllama/llama-7b                                           │ huggyllama                     │ 6.7B  │ 74    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 30.6% │ 2k      │ 2023-04-03  │
│ 🟢 Perfect │ EleutherAI/pythia-12b                                         │ eleutherai                     │ 12.0B │ 74    │ 19.5       │ mlx-8bit │ MLX     │ GPU  │ 52.9% │ 2k      │ 2023-02-28  │
│ 🟢 Perfect │ lmsys/vicuna-13b-v1.5                                         │ LMSYS                          │ 13.0B │ 74    │ 18.0       │ mlx-8bit │ MLX     │ GPU  │ 58.1% │ 4k      │ —           │
│ 🟢 Perfect │ WizardLMTeam/WizardLM-13B-V1.2                                │ WizardLM                       │ 13.0B │ 74    │ 18.0       │ mlx-8bit │ MLX     │ GPU  │ 58.1% │ 4k      │ —           │
│ 🟢 Perfect │ LiquidAI/LFM2.5-1.2B-Instruct                                 │ Liquid AI                      │ 1.2B  │ 73    │ 199.7      │ mlx-8bit │ MLX     │ GPU  │ 12.0% │ 128k    │ 2026-01-06  │
│ 🟢 Perfect │ RedHatAI/Qwen3-32B-NVFP4                                      │ redhatai                       │ 19.1B │ 73    │ 16.5       │ mlx-4bit │ MLX     │ GPU  │ 72.0% │ 40k     │ 2025-06-27  │
│ 🟢 Perfect │ lmstudio-community/QwQ-32B-MLX-8bit                           │ lmstudio-community             │ 9.2B  │ 73    │ 25.4       │ mlx-8bit │ MLX     │ GPU  │ 80.7% │ 131k    │ 2025-03-05  │
│ 🟢 Perfect │ Qwen/Qwen3.5-9B                                               │ Alibaba                        │ 9.7B  │ 73    │ 24.2       │ mlx-8bit │ MLX     │ GPU  │ 84.5% │ 262k    │ 2026-02-27  │
│ 🟢 Perfect │ Qwen/Qwen3.5-9B-Base                                          │ Alibaba                        │ 9.7B  │ 73    │ 24.2       │ mlx-8bit │ MLX     │ GPU  │ 84.5% │ 262k    │ 2026-02-26  │
│ 🟢 Perfect │ cais/HarmBench-Llama-2-13b-cls                                │ cais                           │ 13.0B │ 73    │ 18.0       │ mlx-8bit │ MLX     │ GPU  │ 57.2% │ 2k      │ 2024-02-03  │
│ 🟢 Perfect │ stabilityai/stablelm-2-1_6b-chat                              │ Stability AI                   │ 1.6B  │ 73    │ 142.1      │ mlx-8bit │ MLX     │ GPU  │ 9.2%  │ 4k      │ 2024-04-08  │
│ 🟢 Perfect │ allenai/OLMo-2-0425-1B-Instruct                               │ allenai                        │ 1.5B  │ 73    │ 157.4      │ mlx-8bit │ MLX     │ GPU  │ 8.5%  │ 4k      │ 2025-04-29  │
│ 🟢 Perfect │ Zyphra/Zamba2-1.2B-instruct                                   │ zyphra                         │ 1.2B  │ 73    │ 192.4      │ mlx-8bit │ MLX     │ GPU  │ 7.3%  │ 4k      │ 2024-09-19  │
│ 🟢 Perfect │ LLM360/Amber                                                  │ llm360                         │ 6.7B  │ 73    │ 34.7       │ mlx-8bit │ MLX     │ GPU  │ 30.6% │ 2k      │ 2023-12-07  │
│ 🟢 Perfect │ llm-jp/llm-jp-3.1-13b-instruct4                               │ llm-jp                         │ 13.7B │ 73    │ 17.1       │ mlx-8bit │ MLX     │ GPU  │ 61.1% │ 4k      │ 2025-05-23  │
│ 🟢 Perfect │ LiquidAI/LFM2-VL-3B                                           │ Liquid AI                      │ 3.0B  │ 72    │ 77.9       │ mlx-8bit │ MLX     │ GPU  │ 27.4% │ 128k    │ 2025-10-22  │
│ 🟢 Perfect │ zai-org/glm-4-9b-chat-hf                                      │ zai-org                        │ 9.4B  │ 72    │ 24.9       │ mlx-8bit │ MLX     │ GPU  │ 82.3% │ 131k    │ 2024-10-23  │
│ 🟢 Perfect │ THUDM/glm-4-9b-chat                                           │ thudm                          │ 9.4B  │ 72    │ 24.9       │ mlx-8bit │ MLX     │ GPU  │ 82.3% │ 131k    │ 2024-06-04  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-4B-Thinking-2507-MLX-8bit            │ lmstudio-community             │ 1.1B  │ 72    │ 206.6      │ mlx-8bit │ MLX     │ GPU  │ 16.7% │ 262k    │ 2025-08-06  │
│ 🟢 Perfect │ lmstudio-community/Qwen2.5-Coder-14B-Instruct-MLX-4bit        │ lmstudio-community             │ 2.3B  │ 72    │ 101.3      │ mlx-8bit │ MLX     │ GPU  │ 14.2% │ 32k     │ 2024-11-11  │
│ 🟢 Perfect │ LiquidAI/LFM2-2.6B                                            │ Liquid AI                      │ 2.6B  │ 72    │ 91.0       │ mlx-8bit │ MLX     │ GPU  │ 23.8% │ 128k    │ 2025-09-22  │
│ 🟢 Perfect │ LiquidAI/LFM2-2.6B-Exp                                        │ Liquid AI                      │ 2.6B  │ 72    │ 91.0       │ mlx-8bit │ MLX     │ GPU  │ 23.8% │ 128k    │ 2025-12-25  │
│ 🟢 Perfect │ LiquidAI/LFM2-2.6B-Transcript                                 │ Liquid AI                      │ 2.6B  │ 72    │ 91.0       │ mlx-8bit │ MLX     │ GPU  │ 23.8% │ 128k    │ 2026-01-05  │
│ 🟢 Perfect │ ShahriarFerdoush/llama-3.2-1b-code-instruct                   │ shahriarferdoush               │ 1.2B  │ 72    │ 189.1      │ mlx-8bit │ MLX     │ GPU  │ 12.6% │ 131k    │ 2025-12-24  │
│ 🟢 Perfect │ Qwen/Qwen2.5-1.5B                                             │ Alibaba                        │ 1.5B  │ 72    │ 151.4      │ mlx-8bit │ MLX     │ GPU  │ 15.3% │ 131k    │ 2024-09-15  │
│ 🟢 Perfect │ Qwen/Qwen2-1.5B                                               │ Alibaba                        │ 1.5B  │ 72    │ 151.4      │ mlx-8bit │ MLX     │ GPU  │ 15.3% │ 131k    │ 2024-05-31  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-8B-MLX-8bit                          │ lmstudio-community             │ 2.3B  │ 72    │ 101.5      │ mlx-8bit │ MLX     │ GPU  │ 14.8% │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-14B-MLX-4bit                         │ lmstudio-community             │ 2.3B  │ 72    │ 101.3      │ mlx-8bit │ MLX     │ GPU  │ 14.9% │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ EleutherAI/pythia-6.9b                                        │ eleutherai                     │ 7.0B  │ 72    │ 33.4       │ mlx-8bit │ MLX     │ GPU  │ 31.7% │ 2k      │ 2023-02-14  │
│ 🟢 Perfect │ abaryan/CyberXP_Agent_Llama_3.2_1B                            │ abaryan                        │ 1.2B  │ 72    │ 189.1      │ mlx-8bit │ MLX     │ GPU  │ 12.6% │ 131k    │ 2025-10-07  │
│ 🟢 Perfect │ AdamLucek/Orpo-Llama-3.2-1B-15k                               │ adamlucek                      │ 1.2B  │ 72    │ 189.1      │ mlx-8bit │ MLX     │ GPU  │ 12.6% │ 131k    │ 2024-10-30  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Coder-1.5B-Instruct                              │ Alibaba                        │ 1.5B  │ 72    │ 151.4      │ mlx-8bit │ MLX     │ GPU  │ 10.2% │ 32k     │ 2024-09-18  │
│ 🟢 Perfect │ Qwen/Qwen3-1.7B                                               │ Alibaba                        │ 2.0B  │ 72    │ 115.0      │ mlx-8bit │ MLX     │ GPU  │ 13.3% │ 40k     │ 2025-04-27  │
│ 🟢 Perfect │ Qwen/Qwen3-1.7B-FP8                                           │ Alibaba                        │ 2.0B  │ 72    │ 115.0      │ mlx-8bit │ MLX     │ GPU  │ 13.3% │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ Qwen/Qwen3-1.7B-Base                                          │ Alibaba                        │ 1.7B  │ 72    │ 135.9      │ mlx-8bit │ MLX     │ GPU  │ 11.1% │ 32k     │ 2025-04-28  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-1.7B-MLX-bf16                        │ lmstudio-community             │ 1.7B  │ 72    │ 135.9      │ mlx-8bit │ MLX     │ GPU  │ 11.6% │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ RedHatAI/Qwen2.5-1.5B-quantized.w8a8                          │ redhatai                       │ 1.8B  │ 72    │ 131.5      │ mlx-8bit │ MLX     │ GPU  │ 11.4% │ 32k     │ 2024-10-09  │
│ 🟢 Perfect │ deepseek-ai/deepseek-moe-16b-chat                             │ DeepSeek                       │ 16.4B │ 72    │ 14.3       │ mlx-8bit │ MLX     │ GPU  │ 72.6% │ 4k      │ 2024-01-09  │
│ 🟢 Perfect │ nomic-ai/nomic-embed-text-v1.5                                │ Nomic                          │ 137M  │ 71    │ 1709.6     │ mlx-8bit │ MLX     │ GPU  │ 2.7%  │ 8k      │ 2024-02-10  │
│ 🟢 Perfect │ LaaP-ai/qwen-base-invoicev1.01-1.5B                           │ laap-ai                        │ 1.5B  │ 71    │ 151.4      │ mlx-8bit │ MLX     │ GPU  │ 10.2% │ 32k     │ 2025-07-24  │
│ 🟢 Perfect │ google/gemma-2-2b-it                                          │ Google                         │ 2.6B  │ 71    │ 89.4       │ mlx-8bit │ MLX     │ GPU  │ 13.3% │ 4k      │ 2024-07-16  │
│ 🟢 Perfect │ Efficient-Large-Model/gemma-2-2b-it                           │ efficient-large-model          │ 2.6B  │ 71    │ 89.4       │ mlx-8bit │ MLX     │ GPU  │ 13.7% │ 8k      │ 2024-12-12  │
│ 🟢 Perfect │ google/gemma-2-2b-jpn-it                                      │ Google                         │ 2.6B  │ 71    │ 89.4       │ mlx-8bit │ MLX     │ GPU  │ 13.3% │ 4k      │ 2024-09-25  │
│ 🟢 Perfect │ MilyaShams/T-lite-it-1.0_Q4_0                                 │ milyashams                     │ 2.9B  │ 71    │ 80.0       │ mlx-8bit │ MLX     │ GPU  │ 17.5% │ 32k     │ 2025-01-05  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-8B-MLX-4bit                          │ lmstudio-community             │ 1.3B  │ 71    │ 182.6      │ mlx-8bit │ MLX     │ GPU  │ 9.2%  │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Math-1.5B                                        │ Alibaba                        │ 1.5B  │ 71    │ 151.4      │ mlx-8bit │ MLX     │ GPU  │ 8.7%  │ 4k      │ 2024-09-16  │
│ 🟢 Perfect │ google/gemma-1.1-2b-it                                        │ Google                         │ 2.5B  │ 71    │ 93.3       │ mlx-8bit │ MLX     │ GPU  │ 12.9% │ 4k      │ 2024-03-26  │
│ 🟢 Perfect │ LiquidAI/LFM2-VL-1.6B                                         │ Liquid AI                      │ 1.6B  │ 71    │ 147.5      │ mlx-8bit │ MLX     │ GPU  │ 15.4% │ 128k    │ 2025-08-12  │
│ 🟢 Perfect │ LiquidAI/LFM2.5-VL-1.6B                                       │ Liquid AI                      │ 1.6B  │ 71    │ 146.4      │ mlx-8bit │ MLX     │ GPU  │ 15.5% │ 128k    │ 2026-01-05  │
│ 🟢 Perfect │ meta-llama/Llama-3.2-1B                                       │ Meta                           │ 1.2B  │ 71    │ 189.1      │ mlx-8bit │ MLX     │ GPU  │ 7.4%  │ 4k      │ 2024-09-18  │
│ 🟢 Perfect │ RedHatAI/Qwen3-8B-speculator.eagle3                           │ redhatai                       │ 1.0B  │ 71    │ 228.7      │ mlx-8bit │ MLX     │ GPU  │ 6.5%  │ 4k      │ 2025-09-19  │
│ 🟢 Perfect │ stabilityai/stablelm-3b-4e1t                                  │ Stability AI                   │ 2.8B  │ 71    │ 83.6       │ mlx-8bit │ MLX     │ GPU  │ 14.1% │ 4k      │ 2023-09-29  │
│ 🟢 Perfect │ hmellor/Ilama-3.2-1B                                          │ hmellor                        │ 1.2B  │ 71    │ 189.1      │ mlx-8bit │ MLX     │ GPU  │ 12.6% │ 131k    │ 2025-07-22  │
│ 🟢 Perfect │ LiquidAI/LFM2-1.2B                                            │ Liquid AI                      │ 1.2B  │ 71    │ 199.7      │ mlx-8bit │ MLX     │ GPU  │ 12.0% │ 128k    │ 2025-07-10  │
│ 🟢 Perfect │ LiquidAI/LFM2.5-1.2B-Thinking                                 │ Liquid AI                      │ 1.2B  │ 71    │ 199.7      │ mlx-8bit │ MLX     │ GPU  │ 12.0% │ 128k    │ 2026-01-20  │
│ 🟢 Perfect │ LiquidAI/LFM2.5-1.2B-JP                                       │ Liquid AI                      │ 1.2B  │ 71    │ 199.7      │ mlx-8bit │ MLX     │ GPU  │ 12.0% │ 128k    │ 2026-01-04  │
│ 🟢 Perfect │ LiquidAI/LFM2-1.2B-Tool                                       │ Liquid AI                      │ 1.2B  │ 71    │ 199.7      │ mlx-8bit │ MLX     │ GPU  │ 12.0% │ 128k    │ 2025-09-03  │
│ 🟢 Perfect │ LiquidAI/LFM2-1.2B-RAG                                        │ Liquid AI                      │ 1.2B  │ 71    │ 199.7      │ mlx-8bit │ MLX     │ GPU  │ 12.0% │ 128k    │ 2025-09-03  │
│ 🟢 Perfect │ LiquidAI/LFM2-1.2B-Extract                                    │ Liquid AI                      │ 1.2B  │ 71    │ 199.7      │ mlx-8bit │ MLX     │ GPU  │ 12.0% │ 128k    │ 2025-08-22  │
│ 🟢 Perfect │ LiquidAI/LFM2.5-1.2B-Base                                     │ Liquid AI                      │ 1.2B  │ 71    │ 199.7      │ mlx-8bit │ MLX     │ GPU  │ 12.0% │ 128k    │ 2025-11-28  │
│ 🟢 Perfect │ lmstudio-community/LFM2-1.2B-MLX-bf16                         │ lmstudio-community             │ 1.2B  │ 71    │ 199.7      │ mlx-8bit │ MLX     │ GPU  │ 12.0% │ 128k    │ 2025-07-14  │
│ 🟢 Perfect │ TinyLlama/TinyLlama-1.1B-Chat-v1.0                            │ Community                      │ 1.1B  │ 71    │ 212.5      │ mlx-8bit │ MLX     │ GPU  │ 6.7%  │ 2k      │ 2023-12-30  │
│ 🟢 Perfect │ h2oai/h2ovl-mississippi-2b                                    │ h2oai                          │ 2.2B  │ 71    │ 108.6      │ mlx-8bit │ MLX     │ GPU  │ 11.3% │ 4k      │ 2024-10-15  │
│ 🟢 Perfect │ LGAI-EXAONE/EXAONE-4.0-1.2B                                   │ lgai-exaone                    │ 1.3B  │ 70    │ 182.7      │ mlx-8bit │ MLX     │ GPU  │ 10.2% │ 65k     │ 2025-07-11  │
│ 🟢 Perfect │ Salesforce/xLAM-2-1b-fc-r                                     │ salesforce                     │ 1.5B  │ 70    │ 151.4      │ mlx-8bit │ MLX     │ GPU  │ 10.2% │ 32k     │ 2025-03-27  │
│ 🟢 Perfect │ HuggingFaceTB/SmolLM2-1.7B                                    │ huggingfacetb                  │ 1.7B  │ 70    │ 136.6      │ mlx-8bit │ MLX     │ GPU  │ 9.7%  │ 8k      │ 2024-10-30  │
│ 🟢 Perfect │ bigscience/bloom-1b7                                          │ bigscience                     │ 1.7B  │ 70    │ 135.7      │ mlx-8bit │ MLX     │ GPU  │ 9.5%  │ 4k      │ 2022-05-19  │
│ 🟢 Perfect │ starvector/starvector-1b-im2svg                               │ starvector                     │ 1.4B  │ 70    │ 163.0      │ mlx-8bit │ MLX     │ GPU  │ 8.5%  │ 8k      │ 2025-01-11  │
│ 🟢 Perfect │ LiquidAI/LFM2-Audio-1.5B                                      │ Liquid AI                      │ 1.5B  │ 70    │ 159.0      │ mlx-8bit │ MLX     │ GPU  │ 8.4%  │ 4k      │ 2025-08-28  │
│ 🟢 Perfect │ LiquidAI/LFM2.5-Audio-1.5B                                    │ Liquid AI                      │ 1.5B  │ 70    │ 159.0      │ mlx-8bit │ MLX     │ GPU  │ 8.4%  │ 4k      │ 2025-12-18  │
│ 🟢 Perfect │ allenai/OLMo-2-0425-1B                                        │ allenai                        │ 1.5B  │ 70    │ 157.4      │ mlx-8bit │ MLX     │ GPU  │ 8.5%  │ 4k      │ 2025-04-17  │
│ 🟢 Perfect │ KiteFishAI/Minnow-Math-1.5B                                   │ kitefishai                     │ 1.6B  │ 70    │ 143.1      │ mlx-8bit │ MLX     │ GPU  │ 9.1%  │ 4k      │ 2026-02-12  │
│ 🟢 Perfect │ google/t5gemma-9b-9b-ul2                                      │ Google                         │ 20.3B │ 70    │ 11.5       │ mlx-8bit │ MLX     │ GPU  │ 89.6% │ 4k      │ 2025-06-19  │
│ 🟢 Perfect │ ibm-granite/granite-3b-code-base-2k                           │ ibm-granite                    │ 3.5B  │ 68    │ 67.1       │ mlx-8bit │ MLX     │ GPU  │ 16.8% │ 2k      │ 2024-04-23  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-4B-Instruct-2507-MLX-6bit            │ lmstudio-community             │ 880M  │ 68    │ 265.6      │ mlx-8bit │ MLX     │ GPU  │ 13.4% │ 262k    │ 2025-08-06  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-4B-Instruct-2507-MLX-5bit            │ lmstudio-community             │ 754M  │ 68    │ 309.9      │ mlx-8bit │ MLX     │ GPU  │ 11.8% │ 262k    │ 2025-08-06  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-4B-Instruct-2507-MLX-4bit            │ lmstudio-community             │ 629M  │ 68    │ 371.8      │ mlx-8bit │ MLX     │ GPU  │ 10.2% │ 262k    │ 2025-08-06  │
│ 🟢 Perfect │ nm-testing/tinyllama-oneshot-w8w8-test-static-shape-change    │ nm-testing                     │ 1.1B  │ 68    │ 212.5      │ mlx-8bit │ MLX     │ GPU  │ 6.7%  │ 2k      │ 2024-06-12  │
│ 🟢 Perfect │ EleutherAI/pythia-2.8b                                        │ eleutherai                     │ 2.9B  │ 68    │ 80.3       │ mlx-8bit │ MLX     │ GPU  │ 14.4% │ 2k      │ 2023-02-13  │
│ 🟢 Perfect │ EleutherAI/gpt-neo-2.7B                                       │ eleutherai                     │ 2.7B  │ 68    │ 86.0       │ mlx-8bit │ MLX     │ GPU  │ 13.6% │ 2k      │ 2022-03-02  │
│ 🟢 Perfect │ microsoft/phi-2                                               │ Microsoft                      │ 2.8B  │ 68    │ 84.1       │ mlx-8bit │ MLX     │ GPU  │ 13.9% │ 2k      │ 2023-12-13  │
│ 🟢 Perfect │ OpenPipe/Qwen3-14B-Instruct                                   │ openpipe                       │ 14.8B │ 68    │ 15.8       │ mlx-8bit │ MLX     │ GPU  │ 83.8% │ 40k     │ 2025-10-10  │
│ 🟢 Perfect │ lmstudio-community/DeepSeek-R1-0528-Qwen3-8B-MLX-8bit         │ lmstudio-community             │ 2.3B  │ 68    │ 101.5      │ mlx-8bit │ MLX     │ GPU  │ 21.7% │ 131k    │ 2025-05-29  │
│ 🟢 Perfect │ Qwen/Qwen2.5-0.5B-Instruct                                    │ Alibaba                        │ 494M  │ 67    │ 473.1      │ mlx-8bit │ MLX     │ GPU  │ 4.7%  │ 32k     │ 2024-09-16  │
│ 🟢 Perfect │ Qwen/Qwen2-0.5B-Instruct                                      │ Alibaba                        │ 494M  │ 67    │ 473.1      │ mlx-8bit │ MLX     │ GPU  │ 4.7%  │ 32k     │ 2024-06-03  │
│ 🟢 Perfect │ Gensyn/Qwen2.5-0.5B-Instruct                                  │ gensyn                         │ 494M  │ 67    │ 473.1      │ mlx-8bit │ MLX     │ GPU  │ 4.7%  │ 32k     │ 2025-03-28  │
│ 🟢 Perfect │ Qwen/Qwen1.5-0.5B-Chat                                        │ Alibaba                        │ 620M  │ 67    │ 377.3      │ mlx-8bit │ MLX     │ GPU  │ 5.3%  │ 32k     │ 2024-01-31  │
│ 🟢 Perfect │ HuggingFaceTB/SmolLM-1.7B                                     │ huggingfacetb                  │ 1.7B  │ 67    │ 136.6      │ mlx-8bit │ MLX     │ GPU  │ 9.3%  │ 2k      │ 2024-07-14  │
│ 🟢 Perfect │ EleutherAI/pythia-1.4b                                        │ eleutherai                     │ 1.5B  │ 67    │ 154.3      │ mlx-8bit │ MLX     │ GPU  │ 8.5%  │ 2k      │ 2023-02-09  │
│ 🟢 Perfect │ EleutherAI/gpt-neo-1.3B                                       │ eleutherai                     │ 1.4B  │ 67    │ 171.1      │ mlx-8bit │ MLX     │ GPU  │ 7.9%  │ 2k      │ 2022-03-02  │
│ 🟢 Perfect │ microsoft/phi-1_5                                             │ Microsoft                      │ 1.4B  │ 67    │ 164.8      │ mlx-8bit │ MLX     │ GPU  │ 8.1%  │ 2k      │ 2023-09-10  │
│ 🟢 Perfect │ Qwen/Qwen3-14B                                                │ Alibaba                        │ 14.8B │ 67    │ 15.8       │ mlx-8bit │ MLX     │ GPU  │ 95.9% │ 131k    │ —           │
│ 🟢 Perfect │ Qwen/Qwen2.5-14B                                              │ Alibaba                        │ 14.8B │ 67    │ 15.8       │ mlx-8bit │ MLX     │ GPU  │ 95.9% │ 131k    │ 2024-09-15  │
│ 🟢 Perfect │ allenai/OLMo-1B-hf                                            │ allenai                        │ 1.2B  │ 67    │ 198.6      │ mlx-8bit │ MLX     │ GPU  │ 7.1%  │ 2k      │ 2024-04-12  │
│ 🟢 Perfect │ EleutherAI/pythia-1b                                          │ eleutherai                     │ 1.1B  │ 67    │ 216.7      │ mlx-8bit │ MLX     │ GPU  │ 6.7%  │ 2k      │ 2023-03-10  │
│ 🟢 Perfect │ deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B                     │ DeepSeek                       │ 1.8B  │ 67    │ 131.5      │ mlx-8bit │ MLX     │ GPU  │ 17.3% │ 131k    │ 2025-01-20  │
│ 🟢 Perfect │ lmstudio-community/LFM2.5-1.2B-Instruct-MLX-8bit              │ lmstudio-community             │ 329M  │ 67    │ 709.9      │ mlx-8bit │ MLX     │ GPU  │ 4.9%  │ 128k    │ 2026-01-07  │
│ 🟢 Perfect │ lmstudio-community/ERNIE-4.5-21B-A3B-MLX-4bit                 │ lmstudio-community             │ 21.8B │ 67    │ 14.5       │ mlx-4bit │ MLX     │ GPU  │ 99.8% │ 131k    │ 2025-07-09  │
│ 🟢 Perfect │ lmstudio-community/ERNIE-4.5-21B-A3B-MLX-6bit                 │ lmstudio-community             │ 21.8B │ 67    │ 14.5       │ mlx-4bit │ MLX     │ GPU  │ 99.8% │ 131k    │ 2025-07-10  │
│ 🟢 Perfect │ lmstudio-community/ERNIE-4.5-21B-A3B-MLX-8bit                 │ lmstudio-community             │ 21.8B │ 67    │ 14.5       │ mlx-4bit │ MLX     │ GPU  │ 99.8% │ 131k    │ 2025-07-10  │
│ 🟢 Perfect │ RedHatAI/Mistral-Small-24B-Instruct-2501-FP8-dynamic          │ redhatai                       │ 23.6B │ 67    │ 13.4       │ mlx-4bit │ MLX     │ GPU  │ 81.9% │ 32k     │ 2025-01-30  │
│ 🟢 Perfect │ lmstudio-community/LFM2.5-1.2B-Instruct-MLX-6bit              │ lmstudio-community             │ 256M  │ 66    │ 912.7      │ mlx-8bit │ MLX     │ GPU  │ 4.2%  │ 128k    │ 2026-01-07  │
│ 🟢 Perfect │ tiiuae/Falcon-H1-Tiny-90M-Instruct                            │ TII                            │ 91M   │ 66    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 3.3%  │ 262k    │ 2026-01-12  │
│ 🟢 Perfect │ lmstudio-community/LFM2.5-1.2B-Instruct-MLX-4bit              │ lmstudio-community             │ 183M  │ 66    │ 1277.5     │ mlx-8bit │ MLX     │ GPU  │ 3.6%  │ 128k    │ 2026-01-07  │
│ 🟢 Perfect │ lmstudio-community/DeepSeek-R1-0528-Qwen3-8B-MLX-4bit         │ lmstudio-community             │ 1.3B  │ 66    │ 182.6      │ mlx-8bit │ MLX     │ GPU  │ 13.0% │ 131k    │ 2025-05-29  │
│ 🟢 Perfect │ mistralai/Mistral-Small-24B-Instruct-2501                     │ Mistral AI                     │ 24B   │ 66    │ 13.2       │ mlx-4bit │ MLX     │ GPU  │ 83.3% │ 32k     │ —           │
│ 🟢 Perfect │ allenai/Olmo-3-7B-Instruct                                    │ allenai                        │ 528K  │ 66    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 65k     │ 2025-11-19  │
│ 🟢 Perfect │ HuggingFaceTB/SmolLM2-135M-Instruct                           │ huggingfacetb                  │ 135M  │ 66    │ 1737.7     │ mlx-8bit │ MLX     │ GPU  │ 2.7%  │ 8k      │ 2024-10-31  │
│ 🟢 Perfect │ nvidia/Qwen3-32B-NVFP4                                        │ nvidia                         │ 17.2B │ 66    │ 13.6       │ mlx-8bit │ MLX     │ GPU  │ 97.0% │ 40k     │ 2025-09-09  │
│ 🟢 Perfect │ lmstudio-community/Phi-4-reasoning-plus-MLX-4bit              │ lmstudio-community             │ 2.3B  │ 65    │ 102.0      │ mlx-8bit │ MLX     │ GPU  │ 14.1% │ 32k     │ 2025-05-01  │
│ 🟢 Perfect │ Vikhrmodels/QVikhr-3-1.7B-Instruction-noreasoning             │ vikhrmodels                    │ 1.7B  │ 65    │ 135.9      │ mlx-8bit │ MLX     │ GPU  │ 11.6% │ 40k     │ 2025-05-29  │
│ 🟢 Perfect │ Qwen/Qwen3.5-0.8B                                             │ Alibaba                        │ 873M  │ 65    │ 267.6      │ mlx-8bit │ MLX     │ GPU  │ 13.4% │ 262k    │ 2026-02-28  │
│ 🟢 Perfect │ Qwen/Qwen3.5-0.8B-Base                                        │ Alibaba                        │ 873M  │ 65    │ 267.6      │ mlx-8bit │ MLX     │ GPU  │ 13.4% │ 262k    │ 2026-02-28  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-4B-Thinking-2507-MLX-6bit            │ lmstudio-community             │ 880M  │ 65    │ 265.6      │ mlx-8bit │ MLX     │ GPU  │ 13.4% │ 262k    │ 2025-08-06  │
│ 🟢 Perfect │ Qwen/Qwen2.5-14B-Instruct                                     │ Alibaba                        │ 14.8B │ 65    │ 15.8       │ mlx-8bit │ MLX     │ GPU  │ 95.9% │ 131k    │ —           │
│ 🟢 Perfect │ lmstudio-community/Qwen3-4B-Thinking-2507-MLX-4bit            │ lmstudio-community             │ 629M  │ 65    │ 371.8      │ mlx-8bit │ MLX     │ GPU  │ 10.2% │ 262k    │ 2025-08-06  │
│ 🟢 Perfect │ Qwen/Qwen3-4B-MLX-4bit                                        │ Alibaba                        │ 566M  │ 64    │ 413.1      │ mlx-8bit │ MLX     │ GPU  │ 5.7%  │ 65k     │ 2025-05-23  │
│ 🟢 Perfect │ Qwen/Qwen3-0.6B                                               │ Alibaba                        │ 752M  │ 64    │ 311.0      │ mlx-8bit │ MLX     │ GPU  │ 6.2%  │ 40k     │ 2025-04-27  │
│ 🟢 Perfect │ Qwen/Qwen3Guard-Gen-0.6B                                      │ Alibaba                        │ 752M  │ 64    │ 311.0      │ mlx-8bit │ MLX     │ GPU  │ 6.0%  │ 32k     │ 2025-09-23  │
│ 🟢 Perfect │ Qwen/Qwen3-0.6B-FP8                                           │ Alibaba                        │ 752M  │ 64    │ 311.0      │ mlx-8bit │ MLX     │ GPU  │ 6.2%  │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-1.7B-MLX-8bit                        │ lmstudio-community             │ 484M  │ 64    │ 483.0      │ mlx-8bit │ MLX     │ GPU  │ 4.8%  │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ Qwen/Qwen2.5-0.5B                                             │ Alibaba                        │ 494M  │ 64    │ 473.1      │ mlx-8bit │ MLX     │ GPU  │ 4.7%  │ 32k     │ 2024-09-15  │
│ 🟢 Perfect │ z-lab/Qwen3-4B-DFlash-b16                                     │ z-lab                          │ 537M  │ 64    │ 434.9      │ mlx-8bit │ MLX     │ GPU  │ 5.1%  │ 40k     │ 2026-01-04  │
│ 🟢 Perfect │ Qwen/Qwen1.5-0.5B                                             │ Alibaba                        │ 620M  │ 64    │ 377.3      │ mlx-8bit │ MLX     │ GPU  │ 5.3%  │ 32k     │ 2024-01-22  │
│ 🟢 Perfect │ lmstudio-community/Qwen3-1.7B-MLX-4bit                        │ lmstudio-community             │ 269M  │ 64    │ 869.1      │ mlx-8bit │ MLX     │ GPU  │ 3.6%  │ 40k     │ 2025-04-28  │
│ 🟢 Perfect │ hmellor/tiny-random-LlamaForCausalLM                          │ hmellor                        │ 1M    │ 64    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 8k      │ 2025-04-29  │
│ 🟢 Perfect │ peft-internal-testing/tiny-dummy-qwen2                        │ peft-internal-testing          │ 1M    │ 64    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 32k     │ 2024-07-04  │
│ 🟢 Perfect │ llamafactory/tiny-random-qwen3                                │ llamafactory                   │ 2M    │ 64    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 32k     │ 2026-01-06  │
│ 🟢 Perfect │ tiny-random/qwen3-next-moe                                    │ tiny-random                    │ 3M    │ 64    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 262k    │ 2025-09-12  │
│ 🟢 Perfect │ yujiepan/qwen3-next-moe-tiny-random                           │ yujiepan                       │ 3M    │ 64    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 262k    │ 2025-09-12  │
│ 🟢 Perfect │ llamafactory/tiny-random-Llama-3                              │ llamafactory                   │ 4M    │ 64    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 131k    │ 2024-06-07  │
│ 🟢 Perfect │ michaelbenayoun/llama-2-tiny-4kv-heads-4layers-random         │ michaelbenayoun                │ 9M    │ 64    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 4k      │ 2024-03-28  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Coder-0.5B-Instruct                              │ Alibaba                        │ 494M  │ 64    │ 473.1      │ mlx-8bit │ MLX     │ GPU  │ 4.7%  │ 32k     │ 2024-11-06  │
│ 🟢 Perfect │ Qwen/Qwen2.5-Coder-0.5B                                       │ Alibaba                        │ 494M  │ 64    │ 473.1      │ mlx-8bit │ MLX     │ GPU  │ 4.7%  │ 32k     │ 2024-11-08  │
│ 🟢 Perfect │ LiquidAI/LFM2-700M                                            │ Liquid AI                      │ 742M  │ 64    │ 314.8      │ mlx-8bit │ MLX     │ GPU  │ 8.3%  │ 128k    │ 2025-07-10  │
│ 🟢 Perfect │ google/t5gemma-s-s-prefixlm                                   │ Google                         │ 313M  │ 63    │ 748.0      │ mlx-8bit │ MLX     │ GPU  │ 3.4%  │ 4k      │ 2025-06-19  │
│ 🟢 Perfect │ HuggingFaceTB/SmolLM-135M-Instruct                            │ huggingfacetb                  │ 135M  │ 63    │ 1737.7     │ mlx-8bit │ MLX     │ GPU  │ 2.7%  │ 2k      │ 2024-07-15  │
│ 🟢 Perfect │ google/gemma-3-270m                                           │ Google                         │ 268M  │ 63    │ 871.9      │ mlx-8bit │ MLX     │ GPU  │ 3.2%  │ 4k      │ 2025-08-05  │
│ 🟢 Perfect │ hmellor/tiny-random-Gemma2ForCausalLM                         │ hmellor                        │ 8M    │ 63    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 8k      │ 2025-04-29  │
│ 🟢 Perfect │ TitanML/tiny-mixtral                                          │ titanml                        │ 247M  │ 63    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 131k    │ 2024-04-24  │
│ 🟢 Perfect │ LiquidAI/LFM2-VL-450M                                         │ Liquid AI                      │ 451M  │ 63    │ 518.5      │ mlx-8bit │ MLX     │ GPU  │ 5.9%  │ 128k    │ 2025-08-12  │
│ 🟢 Perfect │ h2oai/h2ovl-mississippi-800m                                  │ h2oai                          │ 826M  │ 63    │ 282.9      │ mlx-8bit │ MLX     │ GPU  │ 5.6%  │ 4k      │ 2024-10-16  │
│ 🟢 Perfect │ lmstudio-community/LFM2-1.2B-MLX-8bit                         │ lmstudio-community             │ 329M  │ 63    │ 709.9      │ mlx-8bit │ MLX     │ GPU  │ 4.9%  │ 128k    │ 2025-07-14  │
│ 🟢 Perfect │ LiquidAI/LFM2-ColBERT-350M                                    │ Liquid AI                      │ 353M  │ 63    │ 661.6      │ mlx-8bit │ MLX     │ GPU  │ 5.1%  │ 128k    │ 2025-10-28  │
│ 🟢 Perfect │ LiquidAI/LFM2-350M                                            │ Liquid AI                      │ 354M  │ 63    │ 659.4      │ mlx-8bit │ MLX     │ GPU  │ 5.1%  │ 128k    │ 2025-07-10  │
│ 🟢 Perfect │ LiquidAI/LFM2-350M-Extract                                    │ Liquid AI                      │ 354M  │ 63    │ 659.4      │ mlx-8bit │ MLX     │ GPU  │ 5.1%  │ 128k    │ 2025-09-03  │
│ 🟢 Perfect │ LiquidAI/LFM2-350M-Math                                       │ Liquid AI                      │ 354M  │ 63    │ 659.4      │ mlx-8bit │ MLX     │ GPU  │ 5.1%  │ 128k    │ 2025-08-25  │
│ 🟢 Perfect │ LiquidAI/LFM2-350M-ENJP-MT                                    │ Liquid AI                      │ 354M  │ 63    │ 659.4      │ mlx-8bit │ MLX     │ GPU  │ 5.1%  │ 128k    │ 2025-09-03  │
│ 🟢 Perfect │ LiquidAI/LFM2-350M-PII-Extract-JP                             │ Liquid AI                      │ 354M  │ 63    │ 659.4      │ mlx-8bit │ MLX     │ GPU  │ 5.1%  │ 128k    │ 2025-09-30  │
│ 🟢 Perfect │ GeneralAnalysis/GA_Guard_Lite                                 │ generalanalysis                │ 596M  │ 63    │ 392.3      │ mlx-8bit │ MLX     │ GPU  │ 4.6%  │ 4k      │ 2025-09-18  │
│ 🟢 Perfect │ openbmb/MiniCPM4-0.5B                                         │ openbmb                        │ 434M  │ 63    │ 538.8      │ mlx-8bit │ MLX     │ GPU  │ 4.4%  │ 32k     │ 2025-06-05  │
│ 🟢 Perfect │ tiiuae/Falcon-H1-0.5B-Base                                    │ TII                            │ 521M  │ 63    │ 448.3      │ mlx-8bit │ MLX     │ GPU  │ 4.5%  │ 16k     │ 2025-05-01  │
│ 🟢 Perfect │ bigscience/bloom-560m                                         │ bigscience                     │ 559M  │ 63    │ 418.0      │ mlx-8bit │ MLX     │ GPU  │ 4.5%  │ 4k      │ 2022-05-19  │
│ 🟢 Perfect │ HuggingFaceTB/SmolLM2-360M                                    │ huggingfacetb                  │ 362M  │ 63    │ 646.0      │ mlx-8bit │ MLX     │ GPU  │ 3.7%  │ 8k      │ 2024-10-31  │
│ 🟢 Perfect │ allenai/Olmo-3-7B-Think                                       │ allenai                        │ 528K  │ 63    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 65k     │ 2025-11-18  │
│ 🟢 Perfect │ katuni4ka/tiny-random-phi3                                    │ katuni4ka                      │ 3M    │ 63    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 4k      │ 2024-04-25  │
│ 🟢 Perfect │ optimum-intel-internal-testing/tiny-random-gpt-oss-mxfp4      │ optimum-intel-internal-testing │ 7M    │ 63    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 131k    │ 2025-10-21  │
│ 🟢 Perfect │ tiiuae/falcon-mamba-tiny-dev                                  │ TII                            │ 9M    │ 63    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 4k      │ 2024-10-13  │
│ 🟢 Perfect │ hmellor/tiny-random-BambaForCausalLM                          │ hmellor                        │ 33M   │ 63    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.5%  │ 262k    │ 2025-04-29  │
│ 🟢 Perfect │ state-spaces/mamba-130m-hf                                    │ state-spaces                   │ 129M  │ 63    │ 1810.1     │ mlx-8bit │ MLX     │ GPU  │ 2.6%  │ 4k      │ 2024-03-06  │
│ 🟢 Perfect │ HuggingFaceTB/SmolLM2-135M                                    │ huggingfacetb                  │ 135M  │ 63    │ 1737.7     │ mlx-8bit │ MLX     │ GPU  │ 2.7%  │ 8k      │ 2024-10-31  │
│ 🟢 Perfect │ bigcode/tiny_starcoder_py                                     │ BigCode                        │ 164M  │ 63    │ 1424.1     │ mlx-8bit │ MLX     │ GPU  │ 2.8%  │ 8k      │ 2023-05-15  │
│ 🟢 Perfect │ Maykeye/TinyLLama-v0                                          │ maykeye                        │ 5M    │ 61    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 2k      │ 2023-07-08  │
│ 🟢 Perfect │ JackFram/llama-160m                                           │ jackfram                       │ 162M  │ 61    │ 1439.2     │ mlx-8bit │ MLX     │ GPU  │ 2.8%  │ 2k      │ 2023-05-26  │
│ 🟢 Perfect │ Joaoffg/ELM                                                   │ joaoffg                        │ 903M  │ 60    │ 258.9      │ mlx-8bit │ MLX     │ GPU  │ 5.9%  │ 2k      │ 2024-05-29  │
│ 🟢 Perfect │ EleutherAI/pythia-410m                                        │ eleutherai                     │ 506M  │ 60    │ 462.0      │ mlx-8bit │ MLX     │ GPU  │ 4.2%  │ 2k      │ 2023-02-13  │
│ 🟢 Perfect │ EleutherAI/pythia-410m-deduped                                │ eleutherai                     │ 506M  │ 60    │ 462.0      │ mlx-8bit │ MLX     │ GPU  │ 4.2%  │ 2k      │ 2023-02-13  │
│ 🟢 Perfect │ bigscience/bloomz-560m                                        │ bigscience                     │ 559M  │ 60    │ 418.0      │ mlx-8bit │ MLX     │ GPU  │ 4.5%  │ 2k      │ 2022-10-08  │
│ 🟢 Perfect │ rinna/japanese-gpt-neox-small                                 │ rinna                          │ 204M  │ 60    │ 1148.0     │ mlx-8bit │ MLX     │ GPU  │ 2.9%  │ 2k      │ 2022-08-31  │
│ 🟢 Perfect │ EleutherAI/pythia-160m-deduped                                │ eleutherai                     │ 213M  │ 60    │ 1099.2     │ mlx-8bit │ MLX     │ GPU  │ 3.0%  │ 2k      │ 2023-02-08  │
│ 🟢 Perfect │ EleutherAI/pythia-14m                                         │ eleutherai                     │ 14M   │ 60    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 2k      │ 2026-02-24  │
│ 🟢 Perfect │ EleutherAI/pythia-14m-deduped                                 │ eleutherai                     │ 39M   │ 60    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.2%  │ 2k      │ 2023-07-19  │
│ 🟢 Perfect │ EleutherAI/pythia-70m-deduped                                 │ eleutherai                     │ 96M   │ 60    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.5%  │ 2k      │ 2023-02-13  │
│ 🟢 Perfect │ peft-internal-testing/opt-125m                                │ peft-internal-testing          │ 125M  │ 60    │ 1866.4     │ mlx-8bit │ MLX     │ GPU  │ 2.6%  │ 2k      │ 2025-11-19  │
│ 🟢 Perfect │ HuggingFaceTB/SmolLM-135M                                     │ huggingfacetb                  │ 135M  │ 60    │ 1737.7     │ mlx-8bit │ MLX     │ GPU  │ 2.7%  │ 2k      │ 2024-07-14  │
│ 🟢 Perfect │ EleutherAI/gpt-neo-125m                                       │ eleutherai                     │ 150M  │ 60    │ 1554.6     │ mlx-8bit │ MLX     │ GPU  │ 2.7%  │ 2k      │ 2022-03-02  │
│ 🟢 Perfect │ AI-Sweden-Models/gpt-sw3-126m                                 │ ai-sweden-models               │ 186M  │ 60    │ 1256.0     │ mlx-8bit │ MLX     │ GPU  │ 2.9%  │ 2k      │ 2022-12-14  │
│ 🟢 Perfect │ bigcode/gpt_bigcode-santacoder                                │ BigCode                        │ 1.1B  │ 60    │ 207.8      │ mlx-8bit │ MLX     │ GPU  │ 6.8%  │ 2k      │ 2023-04-06  │
│ 🟢 Perfect │ stas/tiny-random-llama-2                                      │ stas                           │ 104K  │ 57    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 0k      │ 2023-11-14  │
│ 🟢 Perfect │ MaxJeblick/llama2-0b-unit-test                                │ maxjeblick                     │ 771K  │ 57    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 1k      │ 2023-10-25  │
│ 🟢 Perfect │ lmstudio-community/Phi-4-mini-reasoning-MLX-4bit              │ lmstudio-community             │ 600M  │ 56    │ 389.9      │ mlx-8bit │ MLX     │ GPU  │ 7.2%  │ 131k    │ 2025-05-01  │
│ 🟢 Perfect │ Vamsi/T5_Paraphrase_Paws                                      │ vamsi                          │ 223M  │ 56    │ 1048.7     │ mlx-8bit │ MLX     │ GPU  │ 3.0%  │ 0k      │ 2022-03-02  │
│ 🟢 Perfect │ peft-internal-testing/tiny-random-GPT2LMHeadModel             │ peft-internal-testing          │ 83K   │ 56    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 0k      │ 2025-11-17  │
│ 🟢 Perfect │ peft-internal-testing/tiny-random-gpt2                        │ peft-internal-testing          │ 112K  │ 56    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 0k      │ 2025-11-17  │
│ 🟢 Perfect │ peft-internal-testing/tiny-random-GPTJForCausalLM             │ peft-internal-testing          │ 129K  │ 56    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 0k      │ 2025-11-17  │
│ 🟢 Perfect │ peft-internal-testing/tiny-random-OPTForCausalLM              │ peft-internal-testing          │ 812K  │ 56    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 0k      │ 2025-11-13  │
│ 🟢 Perfect │ SimpleStories/SimpleStories-1.25M                             │ simplestories                  │ 1M    │ 56    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 0k      │ 2025-04-22  │
│ 🟢 Perfect │ arnir0/Tiny-LLM                                               │ arnir0                         │ 13M   │ 56    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 1k      │ 2024-11-03  │
│ 🟢 Perfect │ erwanf/gpt2-mini                                              │ erwanf                         │ 39M   │ 56    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.2%  │ 0k      │ 2024-06-23  │
│ 🟢 Perfect │ gratefulasi/lumeleto                                          │ gratefulasi                    │ 124M  │ 56    │ 1878.4     │ mlx-8bit │ MLX     │ GPU  │ 2.6%  │ 1k      │ 2025-04-24  │
│ 🟢 Perfect │ microsoft/DialoGPT-small                                      │ Microsoft                      │ 176M  │ 56    │ 1331.0     │ mlx-8bit │ MLX     │ GPU  │ 2.8%  │ 1k      │ 2022-03-02  │
│ 🟢 Perfect │ NorthernTribe-Research/UMSR-Reasoner-7B                       │ northerntribe-research         │ 103K  │ 45    │ 2337.5     │ mlx-8bit │ MLX     │ GPU  │ 2.1%  │ 1k      │ 2026-02-23  │
╰────────────┴───────────────────────────────────────────────────────────────┴────────────────────────────────┴───────┴───────┴────────────┴──────────┴─────────┴──────┴───────┴─────────┴─────────────╯
  Note: tok/s values are baseline estimates; real runtime depends on engine/runtime.
