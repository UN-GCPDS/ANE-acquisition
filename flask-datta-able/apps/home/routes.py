#------------------------IMPORTAMOS LIBRERIAS-------------------------#
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, render_template_string
from flask_login import login_required
from urllib.parse import quote, unquote
from jinja2 import TemplateNotFound
from flask import jsonify
from apps.home.sdr_fm_scanner import scan 
from apps.home.water_fall_class import Waterfall 
from apps.home.funciones import fm_audio
import json
import time
import os
#--------------------------------------------------------------------#

@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/<template>')
@login_required
def route_template(template):
    print('--- general ---------------')

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None

@blueprint.route('/start_ppm', methods=['POST'])
@login_required
def start_ppm():
    if request.method == "POST":
        print('----------------start_ppm---------------')
    
        start=time.time()
        print(request.json)
#-------------------DEMODULACION EN FM DE LAS SEÑALES ENCONTRADAS-----------------------#
        lista_frecuencias_encontradas=scan(request.json,plot_waterfall=True)
        #-------------------DEMODULACION EN FM DE LAS SEÑALES ENCONTRADAS-----------------------#
        for signal in lista_frecuencias_encontradas:
            newpath = f".\\apps\static\\assets\\images\\fm_stations\\{signal['freq'] / 1e6}"
            newpath = newpath if os.name == 'nt' else newpath.replace('\\', '/')
            
            if not os.path.exists(newpath):
                os.makedirs(newpath)
        #------------------------PLOTTING WATERFALL SECTION ---------------------------#
            print(f"Band: {signal['freq'] / 1e6} MHz - PSD: {signal['psd']}")
            wf = Waterfall()
            wf.sdr.fc = signal["freq"]
            print(wf.sdr.fc)
            wf.showing_current_station(path=newpath)
            #------------------------demo ---------------------------#
            samples = fm_audio(fc=int(signal["freq"]), plot=True,path=newpath)
    
        data_response = [{'freq': d['freq']/1e6, 'psd': d['psd'],'max pwr': max(d['array']),'min pwr': min(d['array'])} for d in lista_frecuencias_encontradas]

        data_response = json.dumps(data_response)
        data_response = quote(data_response)
        print(data_response)

        segment = get_segment(request)

    #return render_template('home/fm_response.html', segment=segment, data=data_response)
    return redirect(url_for('home_blueprint.fm_response', data=data_response))


@blueprint.route('/fm_response',methods=["GET", "POST"])
@login_required
def fm_response():
    if request.method == 'POST':
        data_response = request.json
        return jsonify(data_response)  # Devolver los datos como JSON
    elif request.method == 'GET':
        data_response = request.args.get('data')
        data_response = unquote(unquote(data_response))
        data_response = json.loads(data_response)
        print(data_response)
        return render_template('home/fm_response.html', segment=get_segment(request), data=data_response)
    else:
        return render_template('home/page-404.html'), 404

@blueprint.route('/example')
def example():
    print('---- solicitud de example: ---------------------')
    return render_template('home/example.html')


