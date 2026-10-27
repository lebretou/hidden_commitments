import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"]="1"
import sys, subprocess, json, time
subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv'], check=True)
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'transformers>=5.8,<6', 'accelerate>=1.10', 'bitsandbytes>=0.48'])
import torch, transformers
from transformers import AutoTokenizer, Qwen3_5ForConditionalGeneration, BitsAndBytesConfig
MODEL_ID = 'Qwen/Qwen3.8-27B'
MODEL_REVISION = '1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0'
print('VERSIONS', torch.__version__, transformers.__version__, flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
model = Qwen3_5ForConditionalGeneration.from_pretrained(
    MODEL_ID, revision=MODEL_REVISION, device_map={'': 0}, dtype=torch.bfloat16,
    quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True),
    attn_implementation='sdpa')
model.eval()
messages=[{'role':'user','content':'Reply with exactly: MODEL_READY'}]
prompt=tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
inputs=tokenizer(prompt, return_tensors='pt').to('cuda')
with torch.inference_mode():
    out=model.generate(**inputs, max_new_tokens=32, do_sample=False)
print(tokenizer.decode(out[0][inputs['input_ids'].shape[-1]:],skip_special_tokens=True))
print('GPU_ALLOCATED_GIB',round(torch.cuda.memory_allocated()/2**30,2))
