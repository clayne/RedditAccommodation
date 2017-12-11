__author__ = 'Sunyam'

import pandas as pd
import numpy as np

'''
- Takes in a dictionary where key is user-pair-tuples and value is a list of conversations involving them.
- Writes all the turns to .txt files

txtFileFormat: userID_ConversationIndex_IndexWithinThatConversation.txt
userID is to identify a user.
ConversationIndex is to indentify a thread.
Index is to identify the comment within a thread.
'''
def write_to_txt(dict_input):   
    conv_index = 0
    for user_pair, conversation in dict_input.items():
        person1 = user_pair[0]
        person2 = user_pair[1]
        for tup in conversation:
            index = conversation.index(tup)
            with open('./accom_try/' + str(person1) + '_' + str(conv_index) + '_' + str(index) + '_.txt', 'wb') as f1:
                f1.write(tup[0])
            with open('./accom_try/' + str(person2) + '_' + str(conv_index) + '_' + str(index) + '_.txt', 'wb') as f2:
                f2.write(tup[1])
        
        conv_index += 1


'''
- Takes in a dictionary where key is user-pair-tuples and value is a list of conversations involving them; stylistic 
  dimension C; path to liwc output
- Returns a dictionary where key is user-pair-tuples and value is accommodation for user2 to user1.
'''
def accommodation_dict(dict_input, C, liwc_path):
    liwc_df = pd.read_csv(liwc_path, delimiter='\t')[['Filename', C]]
    
    total_rows = liwc_df.shape[0]
#     print "Total number of rows in dataframe: ", total_rows
    # Throw an error if this number is not even:
    if total_rows % 2 != 0:
        print "ERROR. Total number of rows in LIWC dataframe: ", total_rows
        return None
    
    accom = {}
    conv_index = 0
    for user_pair, conversation in dict_input.items():
#         print "Users: ", user_pair
        
        ## Calculating Second Probability in eq (2) ##
        total_number_of_replies = len(conversation)
        # Selecting the second user (replier i.e. user_pair[1]) and make sure that it's only the current conversation:
        temp_df_1 = liwc_df.loc[liwc_df.Filename.str.startswith(str(user_pair[1]) + '_' + str(conv_index))]
        c_values_1 = temp_df_1[C].values
        user2_exhibit_C = np.count_nonzero(c_values_1)
        second_term = user2_exhibit_C / float(total_number_of_replies)
#         print replies_with_user2_C
#         print total_number_of_replies
#         print second_term

        ## Calculating First Probability in eq (2) ##
        temp_df_2 = liwc_df.loc[liwc_df.Filename.str.startswith(str(user_pair[0]) + '_' + str(conv_index))]
        c_values_2 = temp_df_2[C].values
        user1_exhibit_C = np.count_nonzero(c_values_2)
        
        df_user2 = liwc_df.loc[liwc_df.Filename.str.startswith(str(user_pair[1]) + '_' + str(conv_index))]
        df_user1 = liwc_df.loc[liwc_df.Filename.str.startswith(str(user_pair[0]) + '_' + str(conv_index))]
        df_concat = pd.concat([df_user2, df_user1])
        
        both_users_exhibit_C = 0.0
        R = df_concat.shape[0]
        
        for k in range(0, (R/2)):
            temp_concatdf = df_concat.loc[df_concat.Filename.str.endswith('_'+str(k)+'_.txt')]
            # temp_concatdf should be of the shape (2,2):
            if temp_concatdf.shape[0] != 2:
                print "Error while calculating bothUsersExhibitC."
                return None
            
            # Both users will exhibit C if 0 is not present in both
            if 0.0 not in temp_concatdf[C].tolist():
                both_users_exhibit_C += 1
                
        first_term = both_users_exhibit_C / float(user1_exhibit_C)
#         print first_term
        
        accom[user_pair] = first_term - second_term
#         print "\n\n"
        conv_index += 1
    
    # Now that we have the accommodation for each user pair, calculating Acc in entire dataset:
    return accom
    
    
'''
- Takes in the accommodation dictionary of the above function.
- Returns the accommodation exhibited in the entire dataset.
'''
def dataset_accom(acc_dict):
    return np.array(acc_dict.values()).mean()

    
# EXAMPLE RUN:
# my = {('user1', 'user2'): [('hi','hello'), ('how are you','good'), ('what else man', 'what do you think')], 
      ('user3', 'user4'): [('who is the best','we are'), ('you do not say','i will do whatever')],
      ('user5', 'user2'): [('who is ','you and me'), ('cmon man','yeah let us do this')]}
# liwc_path = '../../accom_try (14 files)).txt'
# acc_dict = accommodation_dict(my, 'pronoun', liwc_path)
# print acc_dict
# print dataset_accom(acc_dict)
