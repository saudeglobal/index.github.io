from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]  # repo root
TEMPLATE_PATH = ROOT / "content_pipeline" / "templates" / "article_template.html"
OUT_DIR = ROOT / "artigos"

SITE_BASE = "https://saudenaturalglobal.com.br"
AUTHOR = "Equipe Saúde Natural Global"

AMAZON_TAG = "saudenaturalglobal.com.br-20"  # seu ID correto

@dataclass
class Article:
    slug: str
    pillar: str
    title: str
    description: str
    h1: str
    lede: str
    og_image: str
    read_time: str
    cta_title: str
    cta_subtitle: str
    cta_text: str
    cta_url: str
    content_html: str
    evidence_bullets: list[str]

def sanitize_html(s: str) -> str:
    # remove script tags por segurança
    s = re.sub(r"<script.*?>.*?</script>", "", s, flags=re.DOTALL | re.IGNORECASE)
    return s.strip()

def render(template: str, mapping: dict[str, str]) -> str:
    out = template
    for k, v in mapping.items():
        out = out.replace(f"{{{{{k}}}}}", v)
    return out

def make_amazon_search_url(query: str) -> str:
    q = re.sub(r"\s+", "+", query.strip())
    return f"https://www.amazon.com.br/s?k={q}&tag={AMAZON_TAG}"

def build_articles() -> list[Article]:
    today = date.today().isoformat()

    energia_url = make_amazon_search_url("creatina monohidratada")
    imunidade_url = make_amazon_search_url("vitamina d zinco vitamina c")

    return [
        Article(
            slug="energia-mais-disposicao-rotina",
            pillar="Energia",
            title="Energia no dia a dia: hábitos, sono e suplementos com bom custo-benefício | Saúde Natural Global",
            description="Guia prático para ter mais disposição: sono, hidratação, alimentação e opções de suplementos com boa reputação na Amazon.",
            h1="Energia no dia a dia: como ter mais disposição com hábitos simples",
            lede="Para melhorar energia, o básico costuma vencer: sono regular, alimentação consistente, hidratação e movimento. Aqui vai um roteiro simples e opções seguras para começar.",
            og_image="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1600&auto=format&fit=crop",
            read_time="6–8 min",
            cta_title="Quer um impulso com segurança?",
            cta_subtitle="Veja opções populares de creatina e itens relacionados (Amazon Brasil).",
            cta_text="Ver opções na Amazon",
            cta_url=energia_url,
            content_html=sanitize_html("""
<h2>O que mais afeta energia (na prática)</h2>
<p>Antes de pensar em suplemento, ajuste 3 pontos: <strong>sono</strong>, <strong>comida</strong> e <strong>movimento</strong>. Pequenas correções nesses pilares tendem a gerar resultado mais estável do que qualquer “atalho”.</p>

<h2>Checklist rápido (comece hoje)</h2>
<ul>
  <li><strong>Sono:</strong> horário fixo para dormir e acordar (mesmo aos fins de semana).</li>
  <li><strong>Hidratação:</strong> 6–8 copos/dia como base (ajuste por calor/atividade).</li>
  <li><strong>Proteína e fibras:</strong> em pelo menos 2 refeições.</li>
  <li><strong>10–20 min de caminhada</strong> após uma refeição (ajuda energia e disposição).</li>
</ul>

<h2>Suplementos: onde faz sentido</h2>
<p>Se o básico está razoável, alguns suplementos podem ajudar. Para energia e performance, <strong>creatina monohidratada</strong> costuma ser uma opção bem conhecida e com boa relação custo-benefício.</p>

<h3>Como escolher (sem complicação)</h3>
<ul>
  <li>Prefira marcas com boa reputação e avaliações consistentes.</li>
  <li>Evite “blends” cheios de promessas; comece pelo simples.</li>
  <li>Se você tem condição de saúde, usa remédios, está grávida ou amamentando, converse com profissional.</li>
</ul>

<h2>Próximo passo</h2>
<p>Se você quer testar com segurança, use a Amazon como filtro: avaliações, reputação do vendedor e política de devolução.</p>
            """),
            evidence_bullets=[
                "Sono regular e qualidade do sono são determinantes primários de disposição e energia ao longo do dia.",
                "Hidratação e ingestão adequada de proteína ajudam a reduzir fadiga percebida e melhorar desempenho em tarefas diárias.",
                "Creatina monohidratada é amplamente utilizada em contexto de performance; para muitos adultos saudáveis é considerada uma opção comum quando bem orientada."
            ],
        ),
        Article(
            slug="imunidade-rotina-vitamina-d-zinco",
            pillar="Imunidade",
            title="Imunidade: o que realmente ajuda (rotina + nutrientes) | Saúde Natural Global",
            description="Entenda o que mais impacta imunidade: sono, alimentação, vitamina D, zinco e hábitos simples. Guia direto e seguro.",
            h1="Imunidade: rotina simples que faz diferença (e quando pensar em suplementos)",
            lede="Imunidade não é um ‘produto’; é um sistema. Você melhora com sono, alimentação e hábitos consistentes. Quando faz sentido, alguns nutrientes podem complementar.",
            og_image="https://images.unsplash.com/photo-1584467735871-b0e2f56edb0e?q=80&w=1600&auto=format&fit=crop",
            read_time="7–9 min",
            cta_title="Quer comparar opções na Amazon?",
            cta_subtitle="Veja vitamina D, zinco e vitamina C com vendedores bem avaliados.",
            cta_text="Ver opções na Amazon",
            cta_url=imunidade_url,
            content_html=sanitize_html("""
<h2>O básico que sustenta imunidade</h2>
<ul>
  <li><strong>Sono:</strong> privação de sono é um dos maiores sabotadores.</li>
  <li><strong>Alimentação:</strong> variedade de frutas/verduras + proteína adequada.</li>
  <li><strong>Movimento:</strong> atividade leve/moderada com constância.</li>
  <li><strong>Estresse:</strong> crônico e sem descanso tende a piorar resposta do organismo.</li>
</ul>

<h2>Nutrientes comuns quando o objetivo é “reforçar”</h2>
<p>Em geral, vale olhar primeiro para exames e hábitos. Ainda assim, três itens aparecem muito em rotinas de imunidade:</p>
<ul>
  <li><strong>Vitamina D:</strong> relevante em contextos de baixa exposição solar.</li>
  <li><strong>Zinco:</strong> mineral importante em várias funções do organismo.</li>
  <li><strong>Vitamina C:</strong> presente em muitas frutas; suplementação pode ser usada de forma pontual.</li>
</ul>

<h3>Como escolher com segurança</h3>
<ul>
  <li>Evite doses muito acima do recomendado sem orientação.</li>
  <li>Priorize marcas transparentes (rótulo claro, procedência).</li>
  <li>Se usa medicação contínua ou tem condição de saúde, valide com profissional.</li>
</ul>

<h2>Rotina prática (7 dias)</h2>
<ul>
  <li>2 refeições/dia com proteína + vegetal.</li>
  <li>15–20 min de caminhada leve.</li>
  <li>Horário fixo para dormir.</li>
  <li>Se for suplementar, comece simples e monitore como se sente.</li>
</ul>
            """),
            evidence_bullets=[
                "Sono insuficiente tende a prejudicar marcadores relacionados à resposta do organismo.",
                "Deficiências nutricionais específicas (ex.: vitamina D) podem ocorrer em contextos de baixa exposição solar e dieta limitada.",
                "Zinco e vitamina C são nutrientes frequentemente citados em rotinas de suporte, mas a dose e a real necessidade devem ser individualizadas."
            ],
        ),
    ]

def main() -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    articles = build_articles()
    written = 0

    for a in articles:
        canonical = f"{SITE_BASE}/artigos/{a.slug}.html"
        evidence_li = "\n".join([f"<li>{re.escape(x).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}</li>" for x in a.evidence_bullets])

        html = render(template, {
            "TITLE": a.title,
            "DESCRIPTION": a.description,
            "CANONICAL": canonical,
            "OG_TITLE": a.title,
            "OG_IMAGE": a.og_image,
            "PILLAR": a.pillar,
            "H1": a.h1,
            "LEDE": a.lede,
            "READ_TIME": a.read_time,
            "UPDATED_AT": date.today().strftime("%d/%m/%Y"),
            "AUTHOR": AUTHOR,
            "CTA_TITLE": a.cta_title,
            "CTA_SUBTITLE": a.cta_subtitle,
            "CTA_TEXT": a.cta_text,
            "CTA_URL": a.cta_url,
            "CONTENT_HTML": a.content_html,
            "EVIDENCE_BULLETS": evidence_li,
        })

        out_path = OUT_DIR / f"{a.slug}.html"
        out_path.write_text(html, encoding="utf-8")
        written += 1

    print(f"[OK] Generated {written} article(s) in: {OUT_DIR}")

if __name__ == "__main__":
    main()
