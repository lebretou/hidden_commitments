"""Execute with exec(open('colab_run.py').read()) after loading model/tokenizer."""
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import torch
from pilot import Runner, write_scores

ROOT=Path('/content/commitment-pilot')
ROOT.mkdir(exist_ok=True)
torch.manual_seed(848)

def generate(messages,max_new_tokens):
    prompt=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
    inputs=tokenizer(prompt,return_tensors='pt').to('cuda')
    n=inputs['input_ids'].shape[-1]
    if n+max_new_tokens>16384:
        raise ValueError(f'Context budget exceeded ({n} input tokens). No silent truncation allowed.')
    torch.cuda.reset_peak_memory_stats()
    start=time.monotonic()
    with torch.inference_mode():
        out=model.generate(**inputs,max_new_tokens=max_new_tokens,do_sample=False,
                           pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id)
    torch.cuda.synchronize()
    tokens=out[0][n:]
    return {'text':tokenizer.decode(tokens,skip_special_tokens=True),'input_tokens':n,
            'output_tokens':len(tokens),'generation_seconds':time.monotonic()-start,
            'peak_gpu_gib':torch.cuda.max_memory_allocated()/2**30,
            'hit_output_limit':len(tokens)>=max_new_tokens}

versions={p:importlib.metadata.version(p) for p in ['torch','transformers','accelerate','bitsandbytes','huggingface_hub']}
config={'model':MODEL_ID,'revision':MODEL_REVISION,'seed':848,'quantization':'NF4 double quantization',
        'compute_dtype':'bfloat16','thinking':False,'do_sample':False,'context_limit':16384,
        'versions':versions,'gpu':torch.cuda.get_device_name(0),'chunk_characters':2200}
(ROOT/'environment.json').write_text(json.dumps({'configuration':config,'python':sys.version,
    'nvidia_smi':subprocess.check_output(['nvidia-smi'],text=True)},indent=2))
examples=json.loads((ROOT/'experiment_inputs.json').read_text())
labels=json.loads((ROOT/'dataset_draft.json').read_text())
runner=Runner(generate,config,ROOT/'results')

# Set SELECT_IDS in the notebook before exec to run a bounded smoke test or resume a subset.
selected=[x for x in examples if x['id'] in SELECT_IDS] if globals().get('SELECT_IDS') else examples
all_results=[]
started=time.monotonic()
for ex in selected:
    if time.monotonic()-started>90*60:
        print('90-minute run budget reached; completed calls are cached.',flush=True)
        break
    print('START',ex['id'],flush=True)
    all_results.append(runner.run_example(ex))
    write_scores(all_results,labels,ROOT/'results')
print('RUN_COMPLETE',len(all_results),'examples',flush=True)
