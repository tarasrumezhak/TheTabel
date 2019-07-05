import tkinter as tk
from tkinter import filedialog
import nltk

import requests
import json
from sklearn.cluster import KMeans
import numpy as np
import pyexcel


class Atestat:
    def __init__(self, file_path):
        self.path = file_path

        self.image = open(self.path, "rb").read()

        self.__grades_dict = None

    @staticmethod
    def _get_word_columns(bboxes):
        '''
        takes output of get_bounding_boxes(image_data, subscription_key) as input
        '''
        boxes = []
        for element in bboxes['regions']:
            for box in element['lines']:
                boxes.append(box)

        boxes_of_words = []
        for box in boxes:
            for b in box['words']:
                boxes_of_words.append(b)

        new_ys = [[int(box['boundingBox'].split(',')[1])] for box in boxes_of_words]
        new_xs = [[int(box['boundingBox'].split(',')[0])] for box in boxes_of_words]

        new_xs_mean = np.mean(new_xs)
        new_ys_mean = np.mean(new_ys)

        filtered_boxes_of_words = []
        new_filtered_xs = []
        new_filtered_ys = []
        for ind in range(len(new_xs)):
            if (new_ys[ind][0] > new_ys_mean) or (new_xs[ind][0] > new_xs_mean):
                new_filtered_xs.append(new_xs[ind])
                new_filtered_ys.append(new_ys[ind])
                filtered_boxes_of_words.append(boxes_of_words[ind])

        X = np.array(new_filtered_xs)
        kmeans = KMeans(n_clusters=4, random_state=0).fit(X.reshape(-1, 1))

        new_boxes_labels = kmeans.labels_
        new_columns_coordinates = [el[0] for el in kmeans.cluster_centers_]

        sorted_columns_coordinates_indices = sorted(range(len(new_columns_coordinates)),
                                                    key=lambda x: new_columns_coordinates[x])

        modified_boxes_labels = [sorted_columns_coordinates_indices[label] for label in new_boxes_labels]
        indices_matrix = []
        for ind in sorted_columns_coordinates_indices:
            indices_matrix.append([i for i, x in enumerate(modified_boxes_labels) if x == ind])

        words_columns = []
        for col_ind in sorted_columns_coordinates_indices:
            words_columns.append([filtered_boxes_of_words[ind]['text'] for ind in indices_matrix[col_ind]])
        return words_columns

    @staticmethod
    def _replace_letters(word):
        correction = {"a": "а", "B": "в", "M": "м", "y": "у", "k": "к",
                      "0": "о", "o": "о", "x": "х", "j": "і", "i": "і",
                      "p": "р", "H": "н", "c": "с", "ф": "ф", "ђ": "і", "—": " ",
                      "3": "з", "K": "к", "E": "Е", "ы": "ь", "_": " ", "Ы": "Б"}
        for letter in word:
            if letter in correction.keys():
                word = word.replace(letter, correction[letter])
        return word.lower().strip()

    @staticmethod
    def _find_min(dct):
        min_distance = min(dct.values())
        for subject, distance in dct.items():
            if distance == min_distance:
                return subject

    def _correct_word(self, word_with_mistake, filename):
        with open(filename, encoding="utf-8") as f:
            subjects = f.readlines()
        distance = {}
        for word in subjects:
            distance[word] = nltk.edit_distance(word_with_mistake.lower(), word[:-1].lower())
        proper_word = self._find_min(distance)
        fail_rate = distance[proper_word] / len(proper_word)
        return proper_word[:-1], fail_rate

    @staticmethod
    def _build_grades_dct(filename):
        with open(filename, encoding="utf-8") as f:
            grades_lst = f.readlines()
        grades = {}
        for value, subject in enumerate(grades_lst):
            grades[subject.strip().replace("\ufeff", "")] = value + 1
        return grades

    def _optimize_grades(self, lst, dct):
        new_lst = lst[0]
        for i in range(len(new_lst) - 1):
            check = str(new_lst[i]) + str(new_lst[i + 1])
            i_error = self._correct_word(self._replace_letters(str(new_lst[i])), "grades_dict.txt")
            i1_error = self._correct_word(self._replace_letters(str(new_lst[i + 1])), "grades_dict.txt")
            mean_i = (i_error[1] + i1_error[1]) / 2
            w = self._correct_word(self._replace_letters(check), "grades_dict.txt")
            if w[0] in dct.keys() and len(check) <= 10 and w[1] < 0.5 and w[1] < mean_i:
                del new_lst[i]
                new_lst.insert(i, w[0])
                del new_lst[i + 1]
                new_lst.insert(i + 1, "error")
        return new_lst

    @staticmethod
    def _get_bounding_boxes(image_data, subscription_key):
        # You must use the same region in your REST call as you used to get your
        # subscription keys. For example, if you got your subscription keys from
        # westus, replace "westcentralus" in the URI below with "westus".
        #
        # Free trial subscription keys are generated in the "westus" region.
        # If you use a free trial subscription key, you shouldn't need to change
        # this region.
        vision_base_url = "https://northeurope.api.cognitive.microsoft.com/vision/v1.0/"

        analyze_url = vision_base_url + "recognizeText"

        # Set image_url to the URL of an image that you want to analyze.

        headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}
        params = {'handwriting': 'false', 'language': 'ru'}
        response = requests.post(analyze_url, headers=headers, params=params, data=image_data)
        response.raise_for_status()

        # The 'analysis' object contains various fields that describe the image. The most
        # relevant caption for the image is obtained from the 'description' property.

        return json.loads(response.text)

    def _atestat_analysis(self):
        subscription_key = "c7357ae6c97a40e495b37f304a8c9745"
        image_data = self.image
        word_columns = self._get_word_columns(self._get_bounding_boxes(image_data, subscription_key))
        grades = []
        grades_dict = self._build_grades_dct("grades_dict.txt")
        word_cols = [word_columns[1] + word_columns[3]]
        word_cols = [self._optimize_grades(word_cols, grades_dict)]
        for col in word_cols:
            for word in col:
                corrected = self._correct_word(self._replace_letters(word), "dictionary2.txt")
                if corrected[0].strip() in grades_dict.keys():
                    grades.append(corrected[0])

        grades = [grades_dict[x] for x in grades]

        mean_grade = np.mean(grades)

        for col in word_cols:
            for word in col:
                corrected = self._correct_word(self._replace_letters(word), "dictionary2.txt")
                if corrected[0].strip() in grades_dict.keys():
                    grades.append(corrected[0])

        with open("subjects.txt", encoding="utf-8") as f:
            subjects = f.readlines()
        subj_grade = {}
        for i in range(len(subjects) - 3):
            subj_grade[subjects[i].strip()] = grades[i]
        dpa_grade = {}
        for i in range(len(subjects) - 3, len(subjects)):
            dpa_grade[subjects[i].strip()] = grades[i]
        atestat_info = {}
        atestat_info['mean_grade'] = mean_grade
        atestat_info['subjects_grades'] = grades
        # atestat_info['dpa_grades'] = dpa_grade

        return atestat_info

    @property
    def grades(self):
        if not self.__grades_dict:
            self.__grades_dict = self._atestat_analysis()
        return self.__grades_dict


def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title="Select the photo of Atestat")
    atestat = Atestat(file_path)
    print(atestat.grades)

    grades = atestat.grades
    grades = [[atestat.grades['mean_grade']] + [grade for grade in atestat.grades['subjects_grades'].values()]]
    print(grades)
    pyexcel.save_as(array=grades, dest_file_name="result1.xlsx", encoding="utf-8")

if __name__ == "__main__":
    main()


