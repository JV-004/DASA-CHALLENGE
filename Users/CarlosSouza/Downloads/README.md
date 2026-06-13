<p align="center">
  <img src="https://img.shields.io/badge/FIAP-Inteligência%20Artificial-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Fase%204-Visão%20Computacional-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/React%20Native-Expo-9cf?style=for-the-badge&logo=expo" />
  <img src="https://img.shields.io/badge/Flask-Backend-lightgrey?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/TensorFlow-2.16-orange?style=for-the-badge&logo=tensorflow" />
</p>

<h1 align="center">🫀 CardioIA — Fase 4</h1>
<h3 align="center">Assistente Cardiológico Virtual com Visão Computacional</h3>

<p align="center">
  Classificação de imagens médicas por CNN com interface mobile · FIAP · 2026
</p>

<p align="center">
  <a href="#-contexto">Contexto</a> ·
  <a href="#-objetivo">Objetivo</a> ·
  <a href="#-dataset">Dataset</a> ·
  <a href="#-arquitetura-do-projeto">Arquitetura</a> ·
  <a href="#-pipeline-de-pré-processamento">Pipeline</a> ·
  <a href="#-modelos-cnn">Modelos</a> ·
  <a href="#-interface-mobile">Mobile</a> ·
  <a href="#-backend-flask">Backend</a> ·
  <a href="#-como-rodar">Como Rodar</a> ·
  <a href="#-estrutura-do-repositório">Estrutura</a> ·
  <a href="#-critérios-de-avaliação">Avaliação</a> ·
  <a href="#-ir-além">Ir Além</a> ·
  <a href="#-grupo">Grupo</a>
</p>

---

> ⚕️ **Aviso Clínico:** Este sistema é um **protótipo educacional** desenvolvido para a disciplina de Inteligência Artificial da FIAP. Os resultados **não devem ser utilizados para diagnóstico clínico real**. Consulte sempre um profissional de saúde habilitado.

---

## 🧠 Contexto

Após estruturarmos o monitoramento contínuo na fase anterior, o **CardioIA** avança para a **análise de dados médicos com Visão Computacional**. O desafio desta fase é desenvolver um protótipo capaz de transformar imagens médicas simuladas em informações interpretáveis, auxiliando a tomada de decisão clínica.

São exploradas técnicas como **Redes Neurais Convolucionais (CNNs)**, pré-processamento de imagens e Transfer Learning com modelos pré-treinados como **VGG16** e **ResNet**, aplicados a um contexto realista de suporte à saúde.

> 💡 **Por que CNN?** Uma CNN detecta bordas, formas e padrões de forma hierárquica — assim como o cérebro humano reconhece objetos. Aplicada à medicina, ela aprende a identificar anomalias em imagens que o olho humano processaria lentamente em escala.

---

## 🎯 Objetivo

O protótipo entrega quatro componentes integrados:

| Componente | Descrição |
|------------|-----------|
| **Pipeline de dados** | Pré-processamento de imagens médicas (Brain Tumor MRI — Kaggle) |
| **Modelos CNN** | CNN do zero + Transfer Learning (VGG16/ResNet) com métricas completas |
| **Interface mobile** | App React Native / Expo para upload e exibição dos resultados |
| **Backend REST** | API Flask com endpoint `/predict` para inferência em tempo real |

---

## 🗂 Dataset

**[Brain Tumor MRI Dataset](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset)** — Kaggle
7.200 imagens de ressonância magnética cerebral, 4 classes balanceadas.

| Classe | Descrição |
|--------|-----------|
| `glioma` | Tumor do tipo glioma |
| `meningioma` | Tumor do tipo meningioma |
| `notumor` | Sem tumor detectado |
| `pituitary` | Tumor na hipófise (glândula pituitária) |

### Distribuição após Pipeline

| Split | Total de Imagens | Imagens por Classe |
|-------|:---:|:---:|
| **Train** | 4.760 | 1.190 |
| **Validation** | 840 | 210 |
| **Test** | 1.600 | 400 |

### Análise Exploratória

| Distribuição do Dataset | Exemplos por Classe |
|:-:|:-:|
| ![Distribuição](data/Figura%201%20—%20distribuicao_dataset.png) | ![Exemplos](data/Figura%202%20-%20exemplos_classes.png) |

| Antes e Depois do Pré-processamento | Dashboard Final |
|:-:|:-:|
| ![Pré-processamento](data/Figura%203%20-%20antes_depois_preprocessamento.png) | ![Dashboard](data/Figura%204%20-%20dashboard_dataset_final.png) |

---

## 🏗 Arquitetura do Projeto

```
Imagem Médica
     │
     ▼
┌──────────────────┐
│   App Expo       │  React Native · galeria ou câmera
│   (mobile)       │
└────────┬─────────┘
         │ POST /predict  (multipart/form-data)
         ▼
┌──────────────────┐
│  Flask Backend   │  Python · pré-processamento · inferência
│    app.py        │
└────────┬─────────┘
         │ model.predict(image_array)
         ▼
┌──────────────────┐
│   Modelo CNN     │  TensorFlow / Keras · arquivo .h5
│   (Keras)        │
└────────┬─────────┘
         │ { classe, confiança, probabilidades }
         ▼
┌──────────────────┐
│  Tela Resultado  │  badge colorido · barras · aviso clínico
└──────────────────┘
```

---

## ⚙️ Pipeline de Pré-processamento

**Responsável:** Tayná Esteves — RM562491
**Notebook Colab:** [Abrir no Google Colab](https://colab.research.google.com/drive/1S-5SZZlKrsEn6lZ6APxJXYsTi5yX8mSX#scrollTo=ISjNHrAtTyMY)

### Etapas do Pipeline

```
Dataset Bruto (512×512, escala de cinza)
       │
       ▼  1. Inspeção
       │     Contagem por classe · distribuição · verificação de integridade
       ▼  2. Conversão RGB
       │     Escala de cinza → 3 canais (compatibilidade com VGG16, ResNet, MobileNet)
       ▼  3. Redimensionamento
       │     224×224 px (padrão das arquiteturas CNN pré-treinadas)
       ▼  4. Normalização
       │     Escala de pixels [0, 1]
       ▼  5. Divisão
       │     Train 70% · Validation 15% · Test 15%
       ▼  6. Geração de Metadados
              data/metadata_dataset.csv
              Colunas: caminho_imagem · classe · split
```

### Formato de Saída

```
data/processed/
├── train/
│   ├── train_glioma.zip        (1.190 imagens)
│   ├── train_meningioma.zip    (1.190 imagens)
│   ├── train_notumor.zip       (1.190 imagens)
│   └── train_pituitary.zip     (1.190 imagens)
├── val/
│   └── val_{classe}.zip        (210 imagens por classe)
└── test/
    └── test_{classe}.zip       (400 imagens por classe)
```

> ⚠️ Os dados compactados por classe superam os limites de arquivo do GitHub. **Extraia localmente** antes de treinar.

---

## 🤖 Modelos CNN

**Responsável:** João — RM565999

### Abordagem 1 — CNN Simples do Zero

Rede treinada do zero com camadas convolucionais progressivas para extração de features.

```python
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(512, activation='relu'),
    Dropout(0.5),
    Dense(4, activation='softmax')   # 4 classes
])
```

### Abordagem 2 — Transfer Learning (VGG16 / ResNet)

Aproveitamento de pesos pré-treinados no ImageNet (14M imagens) com fine-tuning para o domínio médico.

```python
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False   # congela base; fine-tuning posterior

x = GlobalAveragePooling2D()(base_model.output)
x = Dense(256, activation='relu')(x)
x = Dropout(0.4)(x)
output = Dense(4, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)
```

### Métricas de Avaliação

- ✅ Acurácia (por época — curvas de treino e validação)
- ✅ Precisão, Recall e F1-score (por classe)
- ✅ Matriz de confusão (CNN simples vs. Transfer Learning)

> O modelo exportado (`cardioia_model.h5`) deve ser colocado em `models/` para ativar a inferência real no backend.

---

## 📱 Interface Mobile

**Responsável:** Carlos Eduardo — RM566487
**Tecnologias:** React Native · Expo SDK 51 · Expo Router

### Telas

| | Tela Home | Tela Resultado |
|---|---|---|
| **Função** | Upload por galeria ou câmera | Resultado completo da análise |
| **Elementos** | Preview da imagem · botão "Analisar imagem →" · indicador de carregamento | Classe detectada · confiança · barras de probabilidade por classe · badge colorido · aviso clínico obrigatório |

### Fluxo de Uso

```
1. Abrir o app
2. Tocar em "Galeria" ou "Câmera"
3. Selecionar / fotografar a imagem médica
4. Tocar em "Analisar imagem →"
5. Aguardar inferência (indicador de carregamento)
6. Ver resultado: classe · confiança · probabilidades
```

### Código de Cores dos Resultados

| Badge | Classe | Significado |
|-------|--------|-------------|
| 🟢 Verde | `notumor` | Nenhum tumor detectado |
| 🟡 Amarelo | `meningioma` / `pituitary` | Tumor de baixo risco relativo |
| 🔴 Vermelho | `glioma` | Tumor de alto risco relativo |

---

## 🖥 Backend Flask

**Tecnologias:** Python 3.10 · Flask 3.0 · Pillow · NumPy · TensorFlow 2.16

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Verifica se o servidor está ativo e o modelo está carregado |
| `GET` | `/classes` | Retorna a lista de classes do modelo |
| `POST` | `/predict` | Recebe uma imagem e retorna a classificação |

### Exemplo de Resposta — `POST /predict`

```json
{
  "predicted_class": "glioma",
  "confidence": 94.3,
  "probabilities": {
    "glioma": 94.3,
    "meningioma": 2.1,
    "notumor": 2.9,
    "pituitary": 0.7
  },
  "is_placeholder": false
}
```

### Pré-processamento da Imagem no Backend

```python
img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
img = img.resize((224, 224))
arr = np.array(img, dtype=np.float32) / 255.0
return np.expand_dims(arr, axis=0)   # shape: (1, 224, 224, 3)
```

---

## 🚀 Como Rodar

### Pré-requisitos

| Ferramenta | Versão mínima |
|------------|:---:|
| Python | 3.10+ |
| Node.js | 18+ |
| Expo Go (celular) | última versão |

---

### 1. Clone o Repositório

```bash
git clone https://github.com/Carlos566487/CARDIOIA_Fase4.git
cd CARDIOIA_Fase4
```

---

### 2. Backend Flask

```bash
cd cardioia/backend

# Instale as dependências
pip install -r requirements.txt

# (Opcional) Ativar o modelo real de CNN
# 1. Coloque cardioia_model.h5 dentro de models/
# 2. Instale o TensorFlow
pip install tensorflow==2.16.1
# 3. Descomente os blocos marcados em app.py

# Inicie o servidor
python app.py
# → Servidor rodando em http://0.0.0.0:5000
```

**Testar manualmente:**

```bash
# Health check
curl http://localhost:5000/health

# Classificar uma imagem
curl -X POST http://localhost:5000/predict \
  -F "image=@caminho/para/imagem.jpg"
```

---

### 3. App Mobile (Expo)

```bash
cd cardioia/mobile

# Instale as dependências
npm install

# Configure o IP do backend
# Edite app/config/api.js e substitua DEV_IP pelo seu IP local:
#   macOS/Linux: ifconfig | grep "inet "
#   Windows:     ipconfig | findstr "IPv4"

# Inicie o app
npx expo start
```

Escaneie o **QR code** com o app **Expo Go** instalado no celular.

> ⚠️ O celular e o computador precisam estar na **mesma rede Wi-Fi**.

---

### 4. Notebook de Pré-processamento (Google Colab)

Acesse diretamente pelo link:

🔗 [Abrir notebook no Colab](https://colab.research.google.com/drive/1S-5SZZlKrsEn6lZ6APxJXYsTi5yX8mSX#scrollTo=ISjNHrAtTyMY)

---

## 📁 Estrutura do Repositório

```
CARDIOIA_Fase4/
│
├── cardioia/
│   ├── backend/
│   │   ├── app.py                  # API Flask — endpoints /health, /classes, /predict
│   │   └── requirements.txt        # Dependências Python
│   │
│   ├── mobile/
│   │   ├── app/
│   │   │   ├── _layout.jsx         # Configuração de navegação (Expo Router)
│   │   │   ├── index.jsx           # Tela de upload de imagem
│   │   │   ├── result.jsx          # Tela de resultado da classificação
│   │   │   └── config/
│   │   │       └── api.js          # URL do backend (ajustar IP local)
│   │   ├── app.json
│   │   └── package.json
│   │
│   └── README.md                   # Documentação do módulo mobile/backend
│
├── data/
│   ├── metadata_dataset.csv        # Inventário completo (caminho · classe · split)
│   ├── Figura 1 — distribuicao_dataset.png
│   ├── Figura 2 - exemplos_classes.png
│   ├── Figura 3 - antes_depois_preprocessamento.png
│   ├── Figura 4 - dashboard_dataset_final.png
│   ├── raw/                        # Dados brutos (não versionados)
│   └── processed/
│       ├── train/                  # train_{classe}.zip  (4.760 imgs)
│       ├── val/                    # val_{classe}.zip    (840 imgs)
│       └── test/                   # test_{classe}.zip   (1.600 imgs)
│
├── docs/
│   └── relatorio_pipeline.pdf      # Relatório técnico da Parte 1 (1–2 páginas)
│
├── models/
│   └── cardioia_model.h5           # Modelo treinado (não versionado — gerar localmente)
│
├── notebooks/
│   └── 01_preprocessamento_pipeline.ipynb
│
├── outputs/
│   ├── figures/                    # Curvas de loss e acurácia por época
│   ├── metrics/                    # Métricas e matrizes de confusão
│   └── samples/                    # Amostras de predições do conjunto de teste
│
└── scr/
    └── preprocessing.py            # Script Python standalone do pipeline
```

---

## 📊 Critérios de Avaliação

| Critério | Responsável | Pontos |
|----------|-------------|:------:|
| Pipeline de pré-processamento implementado | Tayná — Int. 1 | **3 pts** |
| Treinamento e avaliação de CNN do zero | João — Int. 2 | **2 pts** |
| Implementação de Transfer Learning funcional | João — Int. 2 | **2 pts** |
| Apresentação dos resultados em protótipo | Carlos — Int. 3 | **2 pts** |
| Documentação clara | Endrew — Int. 4 | **1 pt** |
| Trabalho em equipe (2 a 5 integrantes) | Todos | **+1 pt** |
| **Total possível** | | **11 pts** |

---

## 🚀 Ir Além

### Ir Além A — Ética e Governança em Visão Computacional

O dataset **não contém informações demográficas** (idade, sexo, etnia, equipamento, origem hospitalar), o que limita análises de representatividade e impede detectar vieses populacionais.

Pontos abordados no relatório técnico (`docs/relatorio_pipeline.pdf`):
- Identificação de limitações e desbalanceamento do dataset
- Discussão sobre fairness e representatividade em IA na saúde
- Implicações éticas do uso de modelos de visão computacional em contexto clínico
- O modelo deve ser interpretado exclusivamente como **protótipo acadêmico de apoio à decisão**

### Ir Além B — Integração Mobile ✅

Implementação completa da integração mobile com backend:

- Interface React Native com upload via galeria e câmera
- Backend Flask com endpoint `/predict` recebendo imagens reais
- Exibição de classe detectada, nível de confiança e probabilidades por classe
- Aviso clínico embutido em todas as telas de resultado
- Badge colorido para comunicação visual imediata do resultado

---

## 👥 Grupo

| Integrante | RM | Função Principal |
|------------|:---:|-----------------|
| Tayná Esteves | RM562491 | Engenheira de Dados e Pipeline |
| João | RM565999 | Cientista de IA e Modelos CNN |
| Carlos Eduardo | RM566487 | Desenvolvedor de Interface Mobile |
| Endrew Alves | RM563646 | Documentador e Gestor de Entrega |

---

<p align="center">
  <strong>FIAP · 3º Semestre · Inteligência Artificial · 2026</strong>
</p>

<p align="center">
  Desenvolvido com ❤️ para a disciplina de <strong>Inteligência Artificial</strong> da FIAP
</p>
