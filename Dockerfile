# Dockerfile para Bullet Heaven (Pygame)
FROM python:3.12-slim

# Instala dependências do sistema necessárias para SDL2, X11 e Áudio
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    libgl1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    pulseaudio \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código-fonte
COPY . .

# Cria diretório de saves se não existir
RUN mkdir -p saves

# Configura variáveis de ambiente do SDL para vídeo e áudio
ENV DISPLAY=:0
ENV PYTHONUNBUFFERED=1

# Comando padrão para rodar o jogo
CMD ["python", "src/main.py"]
