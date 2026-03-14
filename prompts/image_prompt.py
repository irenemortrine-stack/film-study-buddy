def build_visual_html(theory_name: str, visual_description: str, film_title: str) -> str:
    """Generate a self-contained HTML/CSS visual card for Playwright screenshot."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 512px;
    height: 512px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    font-family: 'Georgia', serif;
    overflow: hidden;
  }}
  .frame {{
    width: 460px;
    height: 460px;
    border: 1px solid rgba(255,255,255,0.15);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    position: relative;
  }}
  .corner {{
    position: absolute;
    width: 20px;
    height: 20px;
    border-color: rgba(255,255,255,0.4);
    border-style: solid;
  }}
  .corner.tl {{ top: 10px; left: 10px; border-width: 1px 0 0 1px; }}
  .corner.tr {{ top: 10px; right: 10px; border-width: 1px 1px 0 0; }}
  .corner.bl {{ bottom: 10px; left: 10px; border-width: 0 0 1px 1px; }}
  .corner.br {{ bottom: 10px; right: 10px; border-width: 0 1px 1px 0; }}
  .theory-name {{
    color: rgba(255,255,255,0.9);
    font-size: 22px;
    letter-spacing: 3px;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 20px;
  }}
  .divider {{
    width: 60px;
    height: 1px;
    background: rgba(255,255,255,0.3);
    margin: 0 auto 20px;
  }}
  .film-title {{
    color: rgba(255,255,255,0.5);
    font-size: 13px;
    letter-spacing: 2px;
    text-align: center;
  }}
  .visual-desc {{
    color: rgba(255,255,255,0.35);
    font-size: 11px;
    text-align: center;
    margin-top: 16px;
    font-style: italic;
    line-height: 1.6;
  }}
</style>
</head>
<body>
  <div class="frame">
    <div class="corner tl"></div>
    <div class="corner tr"></div>
    <div class="corner bl"></div>
    <div class="corner br"></div>
    <div class="theory-name">{theory_name}</div>
    <div class="divider"></div>
    <div class="film-title">{film_title}</div>
    <div class="visual-desc">{visual_description}</div>
  </div>
</body>
</html>"""
