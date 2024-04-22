import muspy
import argparse
import glob
import json 
import os

parser = argparse.ArgumentParser()
parser.add_argument("--data_path", type=str, help="Path to the mid dataset.")
parser.add_argument("--output_path", type=str, help="Path to the output folder.")
args = parser.parse_args()

# Load the dataset
allMids = glob.glob(args.data_path + "/*.mid")

# Load the dataset and convert to a list of Music objects
midDatasets = []
for mid in allMids:
    midDatasets.append((mid, muspy.read(mid)))

# Compute metrics of all midDatasets
# Record all the metrics in a json file like this
# {metrics1:[{"mid1":value1, "mid2":value2, "mid3":value3}, {"mid1":value1, "mid2":value2, "mid3":value3}], metrics2:[{...}]}
# Save the json file to the output folder

def drum_in_pattern_rate(mid):
    return muspy.metrics.drum_in_pattern_rate(mid, "duple")
def drum_pattern_consistency(mid):
    return muspy.metrics.drum_pattern_consistency(mid)
def empty_beat_rate(mid):
    return muspy.metrics.empty_beat_rate(mid)
def empty_measure_rate(mid, measure_resolution):
    return muspy.metrics.empty_measure_rate(mid, measure_resolution)
def groove_consistency(mid, measure_resolution):
    return muspy.metrics.groove_consistency(mid, measure_resolution)
def n_pitch_classes_used(mid):
    return muspy.metrics.n_pitch_classes_used(mid)
def n_pitches_used(mid):
    return muspy.metrics.n_pitches_used(mid)
def pitch_class_entropy(mid):
    return muspy.metrics.pitch_class_entropy(mid)
def pitch_entropy(mid):
    return muspy.metrics.pitch_entropy(mid)
def pitch_in_scale_rate(mid, root, mode_of_scale):
    return muspy.metrics.pitch_in_scale_rate(mid, root, mode_of_scale)
def pitch_range(mid):
    return muspy.metrics.pitch_range(mid)
def polyphony(mid):
    return muspy.metrics.polyphony(mid)
def polyphony_rate(mid, threshold):
    return muspy.metrics.polyphony_rate(mid, threshold)
def scale_consistency(mid):
    return muspy.metrics.scale_consistency(mid)

# embed all the metrics in the list below
functionList = [
    drum_in_pattern_rate,
    drum_pattern_consistency,
    empty_beat_rate,
    empty_measure_rate,
    groove_consistency,
    n_pitch_classes_used,
    n_pitches_used,
    pitch_entropy,
    pitch_in_scale_rate,
    pitch_range,
    polyphony,
    polyphony_rate,
    scale_consistency
]

# threshold for polyphony_rate
threshold = 2

# compute metrics
metrics = {}
for mid in midDatasets:
    metrics[mid[0]] = {}
    for function in functionList:
        if function.__name__ in ["empty_measure_rate", "groove_consistency"]:
            metrics[mid[0]][function.__name__] = function(mid[1], mid[1].resolution)
        elif function.__name__ in ["pitch_in_scale_rate"]:
            metrics[mid[0]][function.__name__] = function(mid[1], mid[1].key_signatures[0].root, mid[1].key_signatures[0].mode)
        elif function.__name__ in ["polyphony_rate"]:
            metrics[mid[0]][function.__name__] = function(mid[1], threshold)
        else:
            metrics[mid[0]][function.__name__] = function(mid[1])

os.makedirs(args.output_path, exist_ok=True)
json.dump(metrics, open(args.output_path + "/metrics.json", "w"))