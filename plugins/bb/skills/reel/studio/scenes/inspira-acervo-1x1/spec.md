# inspira-acervo-1x1

Cena-base da marca Inspira para o `/bb:reel`. Aplica todas as regras de `references/marca-inspira.md` e nasceu do anúncio do Acervo aprovado para o LinkedIn da Fenalaw 2026 (v5, 20/10/2026), sem a parte do evento.

**Filme em uma linha:** uma pergunta ao Acervo da Inspira e a resposta vem com o trecho e a página do parecer.

Formato 1:1 (1080 × 1080), 20 s, grade de 112 BPM (batida a cada 0,536 s), **sem som**: a cena não define `window.BPM`, então o render não sintetiza batida. Com trilha escolhida pela pessoa, ela entra como `audio.wav`. Funciona sem som: toda ideia está escrita na tela.

## Batidas

| Batida  | O que acontece                                                                       | Texto na tela                                                                                           |
| ------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| 0 a 5   | Gancho no campo claro: logo, duas linhas grandes, linha de apoio                     | "Os pareceres do escritório," / "num lugar só" / "Pergunte e o Acervo da Inspira responde."             |
| 5 a 8   | O gancho sobe e o cartão da pasta sobe de baixo: "Pareceres e modelos", 3 documentos | título: "Pergunte ao Acervo" / "em linguagem natural"                                                   |
| 8 a 14  | Cursor clica na barra; a barra vira a caixa de pergunta e a pergunta é digitada      | "Em quanto tempo o cliente precisa comunicar um incidente à ANPD?"                                      |
| 14 a 24 | Enter: a resposta desce da mesma caixa, com a fonte em pílula                        | título: "A resposta já vem" / "com a fonte indicada"                                                    |
| 24 a 32 | Cursor clica na pílula; a página 2 do parecer abre e o trecho do item 3.1 é marcado  | título: "Confira direto na" / "página de origem"                                                        |
| 32 a 37 | Fechamento no mesmo campo claro                                                      | logo; "Teste no" / "seu escritório"; "inspire-se.co"; "IA é fundamento." / "Construa o que vem depois." |

As duas linhas grandes do fechamento e a linha do site mudam a cada filme. A assinatura não muda.

## Elemento contínuo

A barra de pergunta: foco com borda Cornflower, digitação, pulso no Enter, e a resposta nasce colada embaixo dela. Quando a caixa abre, o cartão da pasta recua (escala 0,95 e menos opacidade) em vez de a tela escurecer.

## Dados

Fictícios, do acervo de demonstração: Parecer 07/2026 · Incidente LGPD (3 páginas), Modelo · Comunicação ao titular, Modelo · Procuração ad judicia. A página do parecer leva o aviso "Documento fictício, criado para demonstração". A resposta segue a Resolução CD/ANPD nº 15/2024, arts. 6º e 9º, conferida em 13/10/2026.

## Referência visual

Componentes recriados a partir do Acervo real em app.inspira.legal (lido em 20/10/2026): barra "Faça uma pergunta sobre os documentos desta pasta…" com ⌘K, caixa de pergunta com rodapé navegar, enviar e fechar.
