1. `git clone https://github.com/microsoft/muzic.git`
2. `conda create --name muzic python=3.7`
3. `conda activate muzic`
4. `cd muzic/clamp`
5. `pip install -r requirements`
6. If the system is linux, go to `clamp.py`, change `load_music` function's subprocess command as below:
    `p = subprocess.Popen("python inference/xml2abc.py -m 2 -c 6 -x " + filename, shell=True, stdout=subprocess.PIPE)`
7. copy `inference/music_query.mxl` and paste it into `inference/music_keys/` 
8. `python clamp.py -clamp_model_name sander-wood/clamp-small-1024 -query_modal music -key_modal text -top_n 2`