# Política de Segurança

## Versões com suporte

O Kepler está em desenvolvimento ativo. Enquanto não houver versões estáveis formalmente publicadas, o suporte a correções de segurança se limita à versão mais recente disponível na branch `main`.

| Versão | Suporte de segurança |
| --- | --- |
| Versão mais recente da `main` | Sim |
| Versões antigas ou não mantidas | Não garantido |

Quando forem publicadas versões estáveis, esta tabela deverá ser atualizada para identificar explicitamente quais versões recebem correções.

## Como reportar uma vulnerabilidade

**Não publique vulnerabilidades em Issues, Pull Requests, discussões ou outros canais públicos.** Um relato público pode expor usuários e facilitar a exploração do problema antes da correção.

Use, preferencialmente, o recurso de **relato privado de vulnerabilidades** na aba **Security** do repositório, caso esteja habilitado. Se essa opção não estiver disponível, entre em contato em particular com os mantenedores por um canal privado associado ao repositório. Não inclua detalhes exploráveis em um issue público para solicitar esse contato.

Ao reportar, inclua, quando possível:

- Descrição do problema e do impacto potencial.
- Etapas para reproduzir a falha ou uma prova de conceito segura.
- Versão, commit ou ambiente afetado.
- Logs e evidências relevantes, removendo senhas, tokens, dados pessoais e informações corporativas confidenciais.
- Uma sugestão de mitigação, se houver.

## Tratamento dos relatos

- Os mantenedores buscarão confirmar o recebimento em até **5 dias úteis**.
- Após a triagem, informarão se o relato foi aceito, se são necessárias informações adicionais ou se não foi possível confirmar a vulnerabilidade.
- O prazo para correção dependerá da gravidade, da complexidade e da possibilidade de mitigação.
- A divulgação pública deverá ocorrer de forma coordenada, após existir uma correção ou orientação de mitigação adequada, sempre que viável.
- Não há garantia de um prazo fixo para correção ou de recompensa financeira por relatos.

## Escopo e boas práticas

O Kepler processa dados operacionais e comerciais. Durante testes ou demonstrações de segurança:

- Use somente ambientes e dados para os quais você tenha autorização.
- Não acesse, altere, extraia ou divulgue dados de terceiros.
- Não interrompa serviços nem execute testes destrutivos.
- Não inclua credenciais, dados pessoais ou informações comerciais reais em issues, commits, logs ou provas de conceito.
- Não tente contornar controles de acesso fora de um teste autorizado.

Relatos de boa-fé são bem-vindos. Esta política não concede autorização para atividades que violem leis, contratos ou direitos de terceiros.

## Atualizações desta política

Esta política poderá ser revisada conforme o Kepler amadurecer, receber versões estáveis e definir canais oficiais de suporte.
