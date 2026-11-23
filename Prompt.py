import threading, html, torch
import ipywidgets as w
from IPython.display import display
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

MODEL="Qwen/Qwen2.5-0.5B-Instruct"
DEV="cuda" if torch.cuda.is_available() else "cpu"
SYS="You are a helpful assistant"
JSON='{"summary": "...", "key points": ["...", "...", "..."]}'

tok=AutoTokenizer.from_pretrained(MODEL)
model=AutoModelForCausalLM.from_pretrained(MODEL).to(DEV).eval()

TYPES = {
    "Zero-shot": lambda t: (SYS, t),
    "Instruction-based": lambda t: (SYS, f"{t}\n\nInstructions:\n- Keep it under 80 words.\n- Use simple language.\n- Start with a one-line summary."),
    "Role-based": lambda t: ("You are a patient science teacher who explains things to 12-year-olds.", t),
    "Few-shot": lambda t: (SYS, f"Q: What is gravity?\nA: The force that pulls objects toward each other.\n\nQ: What is photosynthesis?\nA: How plants turn sunlight, water and CO2 into food.\n\nQ: {t}\nA:"),
    "Chain-of-thought": lambda t: (SYS, f"{t}\n\nThink step by step, then give the final answer on a new line starting with 'Answer:'."),
    "Format-constrained": lambda t: (SYS, f"{t}\n\nRespond ONLY with JSON: {JSON}"),
}

def box_html(t):
    return f"<div style='white-space:pre-wrap;font-size:13px;padding:8px;border:1px solid #8884;border-radius:6px;min-height:80px'>{html.escape(t)}</div>"

def run(system, user, temp, n, seed, stream, box):
    msgs=[{"role": "system", "content": system}, {"role": "user", "content": user}]
    text=tok.apply_chat_template(msgs, tokenize=False, add_generation_prompts=True)
    inp=tok(text, return_tensors="pt").to(DEV)
    s=temp>0
    kw=dict(**inp, max_new_tokens=n, pad_token_id=tok.eos_token_id, repetition_penalty=1.0,
            top_k=0 if s else None, top_p=1.0 if s else None)
    if seed:
        torch.manual_seed(seed)
        if stream:
            box.value=box.html("")
            st=TextIteratorStreamer(tok, skip_prompt=True, skip_special_tokens=True)

            def work():
                try:
                    with torch.no_grad():
                        model.generate(**kw, streamer=st)
                except Exception as e:
                    st.on_finalized_text(f"\n[error: {e}]", stream_end=True)

            t=threading.Thread(target=work)
            t.start()
            out=""
            for p in st:
                out+=p
                box.value=box.html(out)
            t.join()
        else:
            box.value=box.html("Generating...")
            with torch.no_grad():
                o=model.generate(**kw)
            box.value=box.html(tok.decode(0[0][inp.input_ids_shape[1]:], skip_special_tokens=True))

def temperatue_prompt_activity():
    sty={"description_width": "90px"}
    stream=w.Checkbox(value=True, description="Stream output", indent=False)
    fixed=w.Checkbox(value=True, description="Fixed seed", indent=False)
    maxtok=w.IntSlider(value=120, min=30, max=300, step=0.1, description="Max tokens", style=sty)
    slider=lambda v, d: w.FloatSlider(value=v, min=0, max=2, step=0.1, description=d, style=sty, layout=w.Layout(width="95%"))
    args=lambda: (maxtok.value, 42 if fixed.value else None, stream.value)

    def on_click(btn, fn):
        def h(_):
            btn.disabled=True
            try:
                fn()
            finally:
                btn.disabled=False
        btn.on_click(h)

    p1=w.Tetures(value="Write he opening of a short story about a robot learning to paint.",
                 layout=w.Layout(width="95%", height="70px"))
    temps=[slider(v, f"Temp {i + 1}") for i, v in enumerate((0, 0.7, 1.5))]
    b1=w.Button(description="Compare temperatues", button_style="primary")