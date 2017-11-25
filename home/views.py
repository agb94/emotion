from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
import json
import os
import mydetective

# Create your views here.
def index(request):
    return render(request, 'home/index.html')

def analysis(request):
    if request.is_ajax():
        crop_root_dir = 'home' + os.path.join(settings.STATIC_URL, 'crop')
        video_file_path = request.GET['videoFile']
        interval_sec = int(request.GET['interval'])
        metadata_file_path = mydetective.get_metadata_file_path(video_file_path, interval_sec=interval_sec)
        if not os.path.exists(metadata_file_path):
            metadata_file_path = mydetective.collect(video_file_path, interval_sec=interval_sec, crop_root_dir=crop_root_dir)
        K = mydetective.cluster(metadata_file_path, crop_root_dir=crop_root_dir)
        metadata = mydetective.parse_metadata_file(metadata_file_path)
        metadata = sorted(list(filter(lambda d: d['centroid'], metadata)), key=lambda d: d['character_id'])
        data = json.dumps({ 'K': K, 'metadata_file_path': metadata_file_path, 'characters': metadata })
        return HttpResponse(data, content_type='application/json')
    else:
        if request.method == "POST":
            qd = request.POST
        elif request.method == "GET":
            qd = request.GET
        return render(request, 'home/analysis.html', { 'videoFile': qd['videoFile'], 'interval': qd['interval'] })

def characters(request):
    metadata_file_path = request.GET['metadata']
    overview_path, clip_path = mydetective.character_analyzer(metadata_file_path)
    overview = mydetective.parse_overview_file(overview_path)
    clip = mydetective.parse_clip_file_to_dict(clip_path)
    return render(request, 'home/characters.html', { 'overview': overview, 'clip': clip, 'metadata': metadata_file_path })

def relationship(request):
    metadata_file_path = request.GET['metadata']
    overview_path, clip_path = mydetective.character_analyzer(metadata_file_path)
    overview = mydetective.parse_overview_file(overview_path)
    sorted_relationships = mydetective.sorted_relationship(metadata_file_path)
    relationships = dict(list(map(lambda t: (t[0], { 'image': t[1]['centroid_image'], 'rels': list() }), overview )))
    for key, value in sorted_relationships:
        a, b = key
        relationships[a]['rels'].append((b, relationships[b]['image'], value))
        relationships[b]['rels'].append((a, relationships[a]['image'], value))
    return render(request, 'home/relationship.html', { 'relationships': relationships, 'metadata': metadata_file_path })

def emotion(request):
    crop_root_dir = crop_root_dir = 'home' + os.path.join(settings.STATIC_URL, 'crop')
    metadata_file_path = request.GET['metadata']
    if 'character_id' in request.GET:
        character_id=int(request.GET['character_id'])
    else:
        character_id = 1
    emotions = mydetective.characters_emotion(metadata_file_path, character_id, crop_root_dir=crop_root_dir, limit = 10)
    return render(request, 'home/emotion.html', { 'metadata': metadata_file_path, 'character_id': character_id, 'emotions': emotions })
