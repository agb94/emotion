from django.shortcuts import render
from django.http import HttpResponse
import json
import mydetective

# Create your views here.
def index(request):
    return render(request, 'home/index.html')

def analysis(request):
    if request.is_ajax():
        videoFile = request.GET['videoFile']
        interval = int(request.GET['interval'])
        metadata_file_path = mydetective.collect(videoFile, interval)
        # metadata_file_path = 'bigbang-5000.tsv'
        K = mydetective.cluster(metadata_file_path)
        data = json.dumps({ 'K': K, 'metadata': metadata_file_path })
        return HttpResponse(data, content_type='application/json')
    else:
        if request.method == "POST":
            qd = request.POST
        elif request.method == "GET":
            qd = request.GET
        return render(request, 'home/analysis.html', { 'videoFile': qd['videoFile'], 'interval': qd['interval'] })

def characters(request):
    metadata_file_path = 'bigbang-5000.tsv'
    overview_path, clip_path = mydetective.character_analyzer(metadata_file_path)
    overview = mydetective.parse_overview_file(overview_path)
    clip = mydetective.parse_clip_file_to_dict(clip_path)
    return render(request, 'home/characters.html', { 'overview': overview, 'clip': clip })

def relationship(request):
    metadata_file_path = 'bigbang-5000.tsv'
    relationships = mydetective.sorted_relationship(metadata_file_path)
    return render(request, 'home/relationship.html', { 'relationships': relationships })

def emotion(request):
    return render(request, 'home/emotion.html')
