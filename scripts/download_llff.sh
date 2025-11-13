# Requires you to have your Kaggle Auth set up (https://www.kaggle.com/docs/api#authentication)
mkdir -p data/llff
kaggle datasets download -d arenagrenade/llff-dataset-full -p data/llff
unzip data/llff/llff-dataset-full.zip -d data/llff