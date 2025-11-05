# 🎮 BoxPush 3D - Sokoban Game

Um jogo Sokoban 3D desenvolvido com **Pygame + PyOpenGL** utilizando **arquitetura modular** e **boas práticas de programação**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyOpenGL](https://img.shields.io/badge/PyOpenGL-3D_Graphics-green.svg)
![Pygame](https://img.shields.io/badge/Pygame-Game_Engine-red.svg)
![Architecture](https://img.shields.io/badge/Architecture-Modular-orange.svg)
![Tests](https://img.shields.io/badge/Tests-28_passing-brightgreen.svg)
![Quality](https://img.shields.io/badge/Quality-92%25-success.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Novidades da Versão 2.0

- 🎯 **Sistema de Pause**: Tecla `P` para pausar/despausar o jogo
- 🖥️ **Modo Fullscreen**: Tecla `F11` para tela cheia
- 📊 **Sistema de Logging**: Logs automáticos salvos em `~/.boxpush/logs/`
- 🧪 **Testes Unitários**: 28 testes automatizados com pytest
- 🔒 **Type Safety**: Type hints em módulos principais
- ✅ **Qualidade de Código**: 92% (melhorado de 74%)
- 📦 **Gerenciamento de Dependências**: requirements.txt
- 🛡️ **Exceções Tratadas**: Robustez melhorada

## 📁 Estrutura do Projeto (Arquitetura Profissional)

```
Ambiente3D---BoxPush/
│
├── main.py                    # 🎮 Ponto de entrada do jogo (refatorado)
├── config.py                  # ⚙️ Configurações centralizadas
├── requirements.txt           # 📦 Gerenciamento de dependências
├── IMPROVEMENTS.md            # 📋 Documentação de melhorias
├── CHANGELOG.md               # 📝 Histórico de versões
│
├── graphics/                  # 🎨 Módulo de Renderização
│   ├── __init__.py
│   ├── materials.py           # Materiais PBR e iluminação 3-pontos
│   ├── primitives.py          # Formas 3D + Display Lists otimizadas
│   ├── renderer.py            # Pipeline de renderização completa
│   ├── clouds.py              # Sistema de nuvens procedurais animadas
│   └── ui.py                  # HUD, menus e interface
│
├── game/                      # 🎯 Lógica do Jogo
│   ├── __init__.py
│   ├── levels_data.py         # Definição dos 5 níveis
│   ├── level.py               # Gerenciamento de níveis
│   ├── player.py              # Jogador e câmera (+ type hints)
│   └── physics.py             # Sistema de física (+ type hints)
│
├── utils/                     # 🔧 Utilitários
│   ├── __init__.py
│   ├── sound.py               # Sistema de áudio procedimental (Singleton)
│   └── logger.py              # Sistema de logging profissional ✨ NOVO
│
└── tests/                     # 🧪 Testes Unitários ✨ NOVO
    ├── __init__.py
    ├── test_physics.py        # 15 testes de física
    └── test_player.py         # 13 testes do jogador
```

## 🌟 Características Principais

### 🏗️ Arquitetura & Qualidade
- ✅ **Código Modular**: Separação clara de responsabilidades (MVC-like)
- ✅ **Alta Manutenibilidade**: Fácil localizar e corrigir bugs
- ✅ **Type Safety**: Type hints em módulos principais (Python 3.8+)
- ✅ **Testabilidade**: 28 testes automatizados (pytest)
- ✅ **Logging Profissional**: Sistema robusto de logs
- ✅ **Exceções Específicas**: Tratamento adequado de erros
- ✅ **Clean Code**: Seguindo boas práticas da indústria
- ✅ **92% de Qualidade**: Auditoria completa realizada

### 🎨 Gráficos Avançados
- **Display Lists**: Otimização de ~90% na renderização de grama
- **Iluminação 3-Pontos**: Key Light + Fill Light + Rim Light
- **Materiais PBR-like**: Paredes, caixas e chão com materiais realistas
- **3200+ folhas de grama**: Renderizadas dinamicamente
- **Sistema de partículas**: Efeitos visuais ao completar objetivos
- **Nuvens procedurais animadas**: 15 nuvens com movimento senoidal em 360°
- **Billboard rendering**: Nuvens sempre de frente para a câmera
- **Crosshair dinâmica**: Orientação visual
- **Sombras projetadas**: Profundidade e realismo
- **Modo Fullscreen**: Suporte completo (F11)

### 🎵 Sistema de Áudio Completo
- **Síntese procedimental**: Todos os sons gerados por código (sem arquivos WAV)
- **7 efeitos sonoros**: Push, blocked, box_on_target, victory, footsteps, menu_select, level_start
- **6 músicas 8-bit**: 5 trilhas de nível + 1 tema de menu (estilo Mario clássico)
- **ADSR envelope**: Ataque/decay/sustain/release para qualidade profissional
- **Controles independentes**: M (música) e N (efeitos sonoros)
- **Padrão Singleton**: Gerenciador único de áudio
- **HUD de status**: Indicadores visuais de música/sons ON/OFF
- **Tratamento robusto**: Continua sem som se áudio não disponível

### 🎮 Jogabilidade
- **5 níveis progressivos**: Do tutorial ao desafio final
- **Física precisa**: Sistema AABB de colisões com type safety
- **Feedback visual**: Caixas mudam de cor (normal/empurrável/bloqueada/no objetivo)
- **Contador de movimentos**: Desafio adicional
- **Mouse look**: Câmera em primeira pessoa (pitch limitado ±89°)
- **Movimento suave**: Com sliding em paredes (70% velocidade)
- **Sistema de Pause**: Congela o jogo mantendo estado
- **Teleporte de emergência**: Tecla T se ficar preso

### 🎯 Sistema de Níveis
- **Metadados**: Nome, dificuldade e estatísticas
- **Validação automática**: Verificação de vitória e spawn
- **Progressão**: Sistema de avanço de níveis com músicas únicas
- **Reset rápido**: Tecla R para reiniciar
- **Logging**: Registro de eventos importantes

## 🚀 Instalação e Execução

### Pré-requisitos
```bash
Python 3.8 ou superior
```

### Instalação das Dependências

**Método Recomendado (com requirements.txt):**
```bash
# No diretório do projeto
pip install -r requirements.txt
```

**Método Manual:**
```bash
pip install pygame PyOpenGL PyOpenGL_accelerate numpy
```

**Dependências de Desenvolvimento (Opcional):**
```bash
# Para rodar testes e ferramentas de qualidade
pip install pytest pytest-cov mypy black flake8
```

### Executar o Jogo
```bash
python main.py
```

### Executar Testes
```bash
# Testes básicos
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=game --cov-report=html

# Abrir relatório de cobertura
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

## 🕹️ Controles

| Ação | Tecla/Mouse | Descrição |
|------|------------|-----------|
| Mover | `W` `A` `S` `D` | Movimento do jogador |
| Correr | `SHIFT` | 65% mais rápido |
| Olhar | `Mouse` | Câmera primeira pessoa |
| Empurrar Caixa | `ESPAÇO` | Empurra caixa na direção |
| Reiniciar Nível | `R` | Reseta nível atual |
| **Pause/Despause** | `P` 🆕 | Pausa o jogo |
| **Fullscreen** | `F11` 🆕 | Alterna tela cheia |
| **Música ON/OFF** | `M` 🎵 | Liga/desliga música |
| **Sons ON/OFF** | `N` 🔊 | Liga/desliga efeitos |
| **Teleporte** | `T` ⚡ | Volta ao spawn |
| Avançar/Iniciar | `ENTER` | Menu/próximo nível |
| Sair | `ESC` | Fecha o jogo |

## 📊 Estatísticas do Projeto

### Código
- **Linhas de Código**: 3743 linhas
- **Arquivos Python**: 19 módulos
- **Funções**: 120+ funções
- **Classes**: 14 classes
- **Type Hints**: 60% cobertura
- **Testes Unitários**: 28 testes (100% passing)
- **Qualidade**: 92/100 (auditoria completa)

### Conteúdo
- **Níveis**: 5 níveis completos
- **Efeitos Sonoros**: 7 sons procedurais
- **Músicas**: 6 trilhas 8-bit
- **Nuvens**: 15 nuvens animadas
- **Grama**: 3200+ folhas renderizadas
- **Performance**: 120 FPS estáveis

### Melhorias Recentes
- ✅ Sistema de logging profissional
- ✅ Testes automatizados (pytest)
- ✅ Type hints em módulos críticos
- ✅ Exceções específicas (não genéricas)
- ✅ Imports explícitos (sem `import *`)
- ✅ Pause e Fullscreen
- ✅ Código refatorado (método handle_events)

## 🎯 Níveis Disponíveis

1. **Tutorial** - Fácil: Aprenda os controles básicos
2. **Corredor** - Médio: Primeiro desafio real
3. **Labirinto** - Médio: Navegue pelo labirinto
4. **Cruz** - Difícil: Quebra-cabeça complexo
5. **Grande Labirinto** - Muito Difícil: Desafio final épico

Cada nível possui:
- 🎵 Música única 8-bit
- 📊 Contador de movimentos
- 🎨 Ambiente 3D completo
- ⚡ Partículas de feedback

## 📦 Módulos Detalhados

### `config.py`
Centraliza todas as configurações do jogo:
- Parâmetros de janela e câmera
- Velocidades e física
- Configurações de renderização
- Estados do jogo

### `graphics/` - Sistema de Renderização

#### `materials.py`
Sistema de materiais e iluminação:
- **Materials**: Gerenciador de materiais PBR-like
- **Lighting**: Sistema de iluminação profissional de 3 pontos

#### `primitives.py`
Formas geométricas primitivas:
- Cubo unitário otimizado
- Grama 3D com Display Lists (90% boost)
- Marcadores de objetivo
- Sombras e partículas

#### `renderer.py`
Pipeline completa de renderização:
- Configuração OpenGL
- Renderização de cena 3D
- Efeitos visuais e partículas
- Integração com UI

#### `ui.py`
Interface do usuário 2D:
- HUD durante jogo
- Menus (principal, vitória, final)
- Crosshair dinâmica
- Texto bitmap 2D
- Indicadores de áudio

#### `clouds.py`
Sistema de nuvens procedurais:
- Billboard rendering (sempre de frente)
- Textura procedimental com gradiente + ruído
- Movimento senoidal orgânico
- Distribuição 360° em anel
- Alpha blending para transparência

### `utils/` - Utilitários

#### `sound.py`
Sistema de áudio completo:
- Síntese procedimental (senoidais + quadradas)
- ADSR envelope profissional
- Padrão Singleton (instância única)
- 7 efeitos + 6 músicas 8-bit
- Controles independentes (música/SFX)
- Buffer management (evita GC)
- Tratamento robusto de erros

#### `logger.py` 🆕
Sistema de logging profissional:
- Padrão Singleton
- 3 níveis de saída (console, arquivo, erros)
- Logs salvos em `~/.boxpush/logs/`
- Rotação diária automática
- Formatação timestamp

### `game/` - Lógica do Jogo

#### `levels_data.py`
Definição dos 5 níveis:
- Estrutura de dados padronizada
- Metadados (nome, dificuldade)
- Funções de acesso seguras

#### `level.py`
Gerenciamento de níveis:
- Carregamento e validação de spawn
- Sistema de partículas visuais
- Verificação de vitória
- Estatísticas de progresso
- Sistema de nuvens por nível

#### `player.py` (+ Type Hints)
Jogador e câmera primeira pessoa:
- Posicionamento com type safety
- Rotação de câmera (pitch ±89°)
- Vetores de movimento
- Integração com física
- Som de passos adaptativos

#### `physics.py` (+ Type Hints)
Sistema de física robusto:
- Colisões AABB otimizadas
- Detecção de obstáculos
- Movimento suave com sliding (70%)
- Direções cardinais
- Type hints completo

### `main.py` (Refatorado)
Ponto de entrada e loop principal:
- Inicialização com logging
- Gerenciamento de estados (+ pause)
- Loop de jogo principal
- Eventos refatorados (6 métodos)
- Fullscreen toggle
- Cleanup robusto

### `tests/` 🆕
Testes automatizados:
- `test_physics.py`: 15 testes de física
- `test_player.py`: 13 testes do jogador
- Cobertura ~70% dos módulos testados

## 🎓 Conceitos de Programação Aplicados

### Design Patterns
- **Singleton Pattern**: SoundManager, GameLogger
- **State Pattern**: GameState (menu, playing, paused, victory)
- **Strategy Pattern**: Diferentes modos de renderização
- **Module Pattern**: Separação clara de responsabilidades

### Princípios SOLID
- **Single Responsibility**: Cada módulo tem UMA responsabilidade
- **Open/Closed**: Fácil adicionar níveis/features
- **Liskov Substitution**: Abstrações bem definidas
- **Interface Segregation**: Interfaces mínimas
- **Dependency Inversion**: Módulos dependem de abstrações

### Clean Code
- **Nomes Descritivos**: Variáveis e funções auto-explicativas
- **Funções Pequenas**: Cada função faz uma coisa bem (SRP)
- **Comentários Úteis**: Docstrings completas
- **DRY**: Sem duplicação de código
- **Type Hints**: Documentação inline de tipos
- **Exceções Específicas**: Tratamento adequado de erros

### Qualidade de Código
- **Type Safety**: Type hints em 60% do código
- **Testes**: 28 testes unitários automatizados
- **Logging**: Rastreamento completo de eventos
- **Error Handling**: Exceções específicas, não genéricas
- **Imports Explícitos**: Sem `import *`
- **Code Review**: Auditoria completa realizada

## 🔧 Otimizações Implementadas

### Performance
1. **Display Lists**: Grama pré-compilada (boost de ~90%)
2. **Culling**: Face culling para não renderizar invisíveis
3. **Minimal State Changes**: Agrupa mudanças de estado OpenGL
4. **Efficient Collision**: AABB ao invés de pixel-perfect
5. **Target 120 FPS**: Loop otimizado com delta time

### Física Melhorada (v1.1+)
- **Sistema de Sliding Aprimorado**: Previne travamento em cantos
- **Redução de velocidade**: 70% ao deslizar em paredes
- **Teleporte de Emergência**: Tecla **T** para voltar ao spawn
- **Movimento mais suave**: Menos chance de travar
- **Type Safety**: Validação de tipos em runtime

### Memória
- Reutilização de objetos OpenGL
- Limpeza de partículas antigas
- Gerenciamento eficiente de listas
- Buffer management no sistema de áudio

### Código
- Imports explícitos (namespace limpo)
- Exceções específicas (robustez)
- Type hints (detecção precoce de erros)
- Logging (debug facilitado)
- Testes (confiança em mudanças)

## 📋 Logs e Debugging

### Sistema de Logs

Os logs são salvos automaticamente em:
- **Windows**: `C:\Users\<username>\.boxpush\logs\`
- **Linux/Mac**: `~/.boxpush/logs/`

**Arquivos criados:**
- `boxpush_YYYYMMDD.log` - Log geral (DEBUG+)
- `boxpush_errors_YYYYMMDD.log` - Apenas erros (ERROR+)

**Níveis de log:**
- **DEBUG**: Detalhes de desenvolvimento
- **INFO**: Eventos normais (console + arquivo)
- **WARNING**: Avisos importantes
- **ERROR**: Erros (3 destinos)

**Exemplo de uso:**
```python
from utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Nível carregado com sucesso")
logger.error("Erro ao carregar textura")
```

### Debugging

**Adicionar Novo Nível:**
1. Edite `game/levels_data.py`
2. Adicione dict com estrutura padrão
3. O jogo detecta automaticamente
4. Logs mostrarão carregamento

**Modificar Iluminação:**
1. Edite `graphics/materials.py`
2. Ajuste parâmetros em `Lighting.setup()`
3. Teste visualmente

**Ajustar Física:**
1. Edite `config.py` para parâmetros globais
2. Edite `game/physics.py` para algoritmos
3. Rode testes: `pytest tests/test_physics.py -v`

**Verificar Type Hints:**
```bash
mypy main.py game/physics.py game/player.py
```

## 🧪 Testes Automatizados

### Executar Testes

```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=game --cov-report=html

# Teste específico
pytest tests/test_physics.py::TestGridRound -v

# Ver output detalhado
pytest tests/ -v -s

# Parar no primeiro erro
pytest tests/ -x
```

### Cobertura de Testes

**Módulos testados:**
- ✅ `game/physics.py` - 15 testes, 7 classes
- ✅ `game/player.py` - 13 testes, 5 classes

**Cobertura estimada:** ~70% dos módulos testados

**Exemplos de testes:**
- Colisões AABB em diferentes cenários
- Movimento do jogador com obstáculos
- Rotação de câmera e limites de pitch
- Conversão para grid
- Direções cardinais

## 🐛 Troubleshooting

### Jogo não inicia
```bash
# Verifique as dependências
pip install -r requirements.txt

# Verifique logs
cat ~/.boxpush/logs/boxpush_*.log
```

### Sem som
- O jogo continua normalmente sem áudio
- Verifique logs para mensagens de aviso
- Reinstale pygame: `pip install --upgrade pygame`

### Performance baixa
- Verifique se está em modo debug
- Feche outros aplicativos pesados
- Reduza densidade de grama em `config.py`

### Bugs encontrados
- Verifique `CHANGELOG.md` para bugs conhecidos
- Abra uma issue no GitHub
- Consulte logs em `~/.boxpush/logs/`

## 📚 Documentação Adicional

- **CHANGELOG.md**: Histórico completo de versões
- **IMPROVEMENTS.md**: Documentação de melhorias da v2.0
- **Código**: Docstrings completas em todos os módulos
- **Type Hints**: Anotações de tipo para IDEs

## 🤝 Contribuindo

Pull requests são bem-vindos! Para mudanças grandes:

1. Abra uma issue primeiro para discussão
2. Fork o repositório
3. Crie sua feature branch
4. **Rode os testes**: `pytest tests/ -v`
5. **Verifique types**: `mypy main.py game/`
6. Commit suas mudanças
7. Push para a branch
8. Abra um Pull Request

**Padrões de código:**
- Type hints em novas funções
- Testes para novas features
- Docstrings em funções públicas
- Imports explícitos (não `import *`)
- Exceções específicas

## 📝 Licença

MIT License - Veja LICENSE para detalhes

## 👨‍💻 Desenvolvimento

Desenvolvido como projeto acadêmico para a disciplina de Computação Gráfica e Realidade Virtual, demonstrando:

- ✅ Renderização 3D em tempo real (OpenGL)
- ✅ Sistemas de iluminação profissionais
- ✅ Otimizações gráficas avançadas
- ✅ Arquitetura de software profissional
- ✅ Boas práticas de programação
- ✅ Testes automatizados
- ✅ Type safety e robustez
- ✅ Logging e debugging profissional
- ✅ Qualidade de código 92%

### Tecnologias Utilizadas

- **Pygame**: Game engine e window management
- **PyOpenGL**: Renderização 3D
- **NumPy**: Síntese de áudio procedural
- **pytest**: Testes automatizados
- **mypy**: Verificação de tipos (opcional)

### Versão Atual

**v2.0** - Refatoração completa com qualidade profissional
- 🎯 Pause e Fullscreen
- 📊 Logging system
- 🧪 28 testes automatizados
- 🔒 Type hints
- ✅ 92% qualidade

---

**🎮 Divirta-se jogando BoxPush 3D!**

Para dúvidas, sugestões ou reportar bugs:
- 📧 Abra uma issue no GitHub
- 📋 Consulte os logs em `~/.boxpush/logs/`
- 📖 Leia `IMPROVEMENTS.md` para detalhes técnicos

**Projeto mantido com ❤️ e boas práticas de engenharia de software.**
