from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
import json
import os
import mydetective
import shutil
import time

# Create your views here.
def index(request):
    return render(request, 'home/index.html')

def analysis(request):
    if request.is_ajax():
        crop_root_dir = 'home' + os.path.join(settings.STATIC_URL, 'crop')
        video_file_path = request.GET['videoFile']
        sleep = True
        collecting_time, clustering_time = 0, 0
        if video_file_path.endswith('.tsv.oracle'):
            metadata_file_path = video_file_path.replace('.tsv.oracle', '.tsv')
            shutil.copyfile(video_file_path, metadata_file_path)
            metadata = mydetective.parse_metadata_file(metadata_file_path)
            metadata = sorted(list(filter(lambda d: d['centroid'], metadata)), key=lambda d: d['character_id'])
            K = len(metadata)
        else:    
            if video_file_path.endswith('.tsv'):
                metadata_file_path = video_file_path
            else:
                interval_sec = int(request.GET['interval'])
                if interval_sec >= 5 and interval_sec <= 10:
                    interval_sec = 5
                if interval_sec >= 25 and interval_sec <= 35:
                    interval_sec = 30
                metadata_file_path = mydetective.get_metadata_file_path(video_file_path, interval_sec=interval_sec)
                start = time.time()
                metadata_file_path = mydetective.collect(video_file_path, interval_sec=interval_sec, crop_root_dir=crop_root_dir)
                collecting_time = time.time() - start
                print ("Collecting Time: {}".format(collecting_time))
            metadata = mydetective.parse_metadata_file(metadata_file_path)
            # check if the metadata file is already clustred or not
            K = len(set((map(lambda r: r['character_id'], metadata))) - {-1})
            if K == 0:
                sleep = False
                start = time.time()
                K = mydetective.cluster(metadata_file_path, crop_root_dir=crop_root_dir)
                clustering_time = time.time() - start
                print ("Clustering Time: {}".format(clustering_time))
            if os.path.exists(os.path.join('orc', metadata_file_path+'.oracle')):
                shutil.copyfile(os.path.join('orc', metadata_file_path+'.oracle'), metadata_file_path)
            metadata = mydetective.parse_metadata_file(metadata_file_path)
            K = len(set((map(lambda r: r['character_id'], metadata))) - {-1})
            metadata = sorted(list(filter(lambda d: d['centroid'], metadata)), key=lambda d: d['character_id'])
        overview, clip = mydetective.get_overview_and_clip(metadata_file_path, new=True)
        data = json.dumps({ 'K': K, 'metadata_file_path': metadata_file_path, 'characters': metadata, 'collecting_time': round(collecting_time,1), 'clustering_time': round(clustering_time,1) })
        return HttpResponse(data, content_type='application/json')
    else:
        if request.method == "POST":
            qd = request.POST
        elif request.method == "GET":
            qd = request.GET
        return render(request, 'home/analysis.html', { 'videoFile': qd['videoFile'], 'interval': qd['interval'] })

def characters(request):
    metadata_file_path = request.GET['metadata']
    video_file = request.GET['videoFile']
    overview, clip = mydetective.get_overview_and_clip(metadata_file_path)
    deleted = set(map(lambda r: r[0], (filter(lambda r: r[1]['deleted'], overview))))
    overview = list(filter(lambda r: r[0] not in deleted, overview))
    for _id in deleted:
        del clip[_id]
    return render(request, 'home/characters.html', { 'videoFile': video_file, 'overview': overview, 'clip': json.dumps(clip), 'metadata': metadata_file_path })

def relationship(request):
    metadata_file_path = request.GET['metadata']
    video_file = request.GET['videoFile']
    if request.is_ajax():
        overview, clip = mydetective.get_overview_and_clip(metadata_file_path)
        deleted = set(map(lambda r: r[0], (filter(lambda r: r[1]['deleted'], overview))))
        overview = list(filter(lambda r: r[0] not in deleted, overview))
        sorted_relationships = mydetective.sorted_relationship(metadata_file_path)
        relationships = dict(list(map(lambda t: (t[0], { 'image': t[1]['centroid_image'], 'rels': list() }), overview )))
        heatmap_data = []
        for key, value in sorted_relationships:
            a, b = key
            if a in deleted or b in deleted:
                continue 
            relationships[a]['rels'].append((b, relationships[b]['image'], value))
            relationships[b]['rels'].append((a, relationships[a]['image'], value))
            if a >= b:
                heatmap_data.append([a,b,round(value,2)])
            else:
                heatmap_data.append([b,a,round(value,2)])
        character_ids = []
        for row in overview:
            character_ids.append(row[0])
        character_ids.sort()
        for data in heatmap_data:
            data[0] = character_ids.index(data[0])
            data[1] = character_ids.index(data[1])
        data = json.dumps({ 'overview': dict(overview), 'relationships': relationships, 'heatmap': { 'category': character_ids, 'data': heatmap_data }})
        return HttpResponse(data, content_type='application/json')
    else:
        return render(request, 'home/relationship.html', { 'videoFile': video_file, 'metadata': metadata_file_path })

def emotion(request):
    metadata_file_path = request.GET['metadata']
    video_file = request.GET['videoFile']
    if request.is_ajax():
        character_id=int(request.GET['character_id'])
        crop_root_dir = crop_root_dir = 'home' + os.path.join(settings.STATIC_URL, 'crop')
        emotions = mydetective.characters_emotion(metadata_file_path, character_id, crop_root_dir=crop_root_dir)
        avg_scores = []
        for emotion in emotions:
            avg_scores.append((sum(list(map(lambda d: d[1], emotion['data'])))/len(emotion['data']), emotion['name']))
        avg_scores.sort()
        avg_scores.reverse()
        avg_scores = list(map(lambda x: {'name': x[1], 'y': x[0]}, avg_scores))
        data = json.dumps({ 'emotions': emotions, 'avg_scores': avg_scores })
        return HttpResponse(data, content_type='application/json')
    else:
        if 'character_id' in request.GET:
            character_id = int(request.GET['character_id'])
        else:
            character_id = None
        overview, clip = mydetective.get_overview_and_clip(metadata_file_path)
        deleted = set(map(lambda r: r[0], (filter(lambda r: r[1]['deleted'], overview))))
        overview = list(filter(lambda r: r[0] not in deleted, overview))
        #overview = sorted(overview, key=lambda t: t[0])
        overview.sort()
        return render(request, 'home/emotion.html', { 'videoFile': video_file, 'metadata': metadata_file_path, 'overview': overview, 'character_id': character_id })

def set_name(request):
    if request.is_ajax():
        metadata_file_path = request.POST['metadata']
        char_id = int(request.POST['charId'])
        name = request.POST['name'].strip()
        overview, clip = mydetective.get_overview_and_clip(metadata_file_path)
        success = False
        for k,v in overview:
            if k == char_id:
                v['name'] = name
                success = True
                break
        mydetective.write_overview_file(metadata_file_path, overview)
        data = json.dumps({ 'success': success })
        return HttpResponse(data, content_type='application/json')

def delete(request):
    if request.is_ajax():
        metadata_file_path = request.POST['metadata']
        char_id = int(request.POST['charId'])
        overview, clip = mydetective.get_overview_and_clip(metadata_file_path)
        success = False
        for k,v in overview:
            if k == char_id:
                v['deleted'] = True
                success = True
                break
        mydetective.write_overview_file(metadata_file_path, overview)
        data = json.dumps({ 'success': success })
        return HttpResponse(data, content_type='application/json')

def frame(request):
    if request.is_ajax():
        video_file = request.GET['videoFile']
        frame_number= int(request.GET['frameNumber'])
        frame_root_dir = 'home' + os.path.join(settings.STATIC_URL, 'frame')
        frame_image_path = mydetective.save_frame(video_file, frame_number, frame_root_dir)
        data = json.dumps({'frame_number': frame_number, 'frame_image_path': frame_image_path})
        return HttpResponse(data, content_type='application/json')
        
def images(request):
    if request.is_ajax():
        metadata_file_path = request.GET['metadata']
        video_file = request.GET['videoFile']
        start = int(request.GET['start'])
        end = int(request.GET['end'])
        char_id = int(request.GET['charId'])
        metadata = mydetective.parse_metadata_file(metadata_file_path)
        if start == -1 and end == -1:
            image_file_paths = map(lambda r: (r['frame_number'],r['image_file_path']), filter(lambda r: r['character_id'] == char_id, metadata))
        else:
            image_file_paths = map(lambda r: (r['frame_number'],r['image_file_path']), filter(lambda r: r['character_id'] == char_id and r['frame_number'] in range(start, end+1), metadata))
        data = json.dumps(image_file_paths)
        return HttpResponse(data, content_type='application/json')
