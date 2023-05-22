
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
sys.path.insert(0, os.path.abspath('..'))
import numpy as np
from art.attacks.inference.membership_inference import MembershipInferenceBlackBox
from art.attacks.inference.membership_inference import ShadowModels
from art.utils import to_categorical
from art.estimators.classification.scikitlearn import ScikitlearnSVC

# import the dataset (with the headers)
df = pd.read_csv('./datasets/training/balanced/membership_inference_noisy.csv', header=0, sep=',')

# define the scaler
scaler = StandardScaler()

# get X and y values from the dataset
X = df.loc[:, ['Lux', 'Float time value']]
y = df['Label']

# convert to numpy array
X = X.values
y = y.values

# split the data into train and test datasets
# 70% for training, 30% for predictions
x_target, x_shadow, y_target, y_shadow = train_test_split(X, y, test_size=0.70,random_state=0)
#(x_target, y_target), (x_shadow, y_shadow), _, _ = load_nursery(test_set=0.75)

target_train_size = len(x_target) // 2
x_target_train = scaler.fit_transform(x_target[:target_train_size])
y_target_train = y_target[:target_train_size]
x_target_test = scaler.transform(x_target[target_train_size:])
y_target_test = y_target[target_train_size:]

# SVM

# for the actual tests linear svm was used (kernel="linear")
# but to check the approximate increase/decrease in the attack success rates
# the kernel can be changed to rbf
model = SVC(kernel="linear", C=100)
model.fit(x_target_train, y_target_train)

art_classifier = ScikitlearnSVC(model)


#print('Base model accuracy:', model.score(x_target_test, y_target_test))


shadow_models = ShadowModels(art_classifier, num_shadow_models=3, random_state=10)

shadow_dataset = shadow_models.generate_shadow_dataset(x_shadow, to_categorical(y_shadow, 2))
(member_x, member_y, member_predictions), (nonmember_x, nonmember_y, nonmember_predictions) = shadow_dataset

# Shadow models' accuracy
print([sm.model.score(x_target_test, y_target_test) for sm in shadow_models.get_shadow_models()])


# ATTACK

attack = MembershipInferenceBlackBox(art_classifier, attack_model_type="rf")
attack.fit(member_x, member_y, nonmember_x, nonmember_y, member_predictions, nonmember_predictions)
member_infer = attack.infer(x_target_train, y_target_train)
nonmember_infer = attack.infer(x_target_test, y_target_test)

member_acc = np.sum(member_infer) / len(x_target_train)
nonmember_acc = 1 - np.sum(nonmember_infer) / len(x_target_test)
acc = (member_acc * len(x_target_train) + nonmember_acc * len(x_target_test)) / (len(x_target_train) + len(x_target_test))
#print('Attack Member Acc:', member_acc)
#print('Attack Non-Member Acc:', nonmember_acc)
print('Attack Accuracy:', acc)


def calc_precision_recall(predicted, actual, positive_value=1):
    score = 0  # both predicted and actual are positive
    num_positive_predicted = 0  # predicted positive
    num_positive_actual = 0  # actual positive
    for i in range(len(predicted)):
        if predicted[i] == positive_value:
            num_positive_predicted += 1
        if actual[i] == positive_value:
            num_positive_actual += 1
        if predicted[i] == actual[i]:
            if predicted[i] == positive_value:
                score += 1

    if num_positive_predicted == 0:
        precision = 1
    else:
        precision = score / num_positive_predicted  # the fraction of predicted “Yes” responses that are correct
    if num_positive_actual == 0:
        recall = 1
    else:
        recall = score / num_positive_actual  # the fraction of “Yes” responses that are predicted correctly

    return precision, recall


#print(calc_precision_recall(np.concatenate((member_infer, nonmember_infer)),
#                            np.concatenate((np.ones(len(member_infer)), np.zeros(len(nonmember_infer))))))


from art.attacks.inference.membership_inference import MembershipInferenceBlackBoxRuleBased

baseline = MembershipInferenceBlackBoxRuleBased(art_classifier)

bl_inferred_train = baseline.infer(x_target_train, y_target_train)
bl_inferred_test = baseline.infer(x_target_test, y_target_test)

bl_member_acc = np.sum(bl_inferred_train) / len(bl_inferred_train)
bl_nonmember_acc = 1 - (np.sum(bl_inferred_test) / len(bl_inferred_test))
bl_acc = (bl_member_acc * len(bl_inferred_train) + bl_nonmember_acc * len(bl_inferred_test)) / (len(bl_inferred_train) + len(bl_inferred_test))
#print(bl_member_acc)
#print(bl_nonmember_acc)
print('Baseline Accuracy:', bl_acc)

#print(calc_precision_recall(np.concatenate((bl_inferred_train, bl_inferred_test)),
#                            np.concatenate((np.ones(len(bl_inferred_train)), np.zeros(len(bl_inferred_test))))))
