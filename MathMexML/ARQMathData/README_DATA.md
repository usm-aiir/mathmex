# Table of Contents  
[ARQMath Lab at CLEF](#arqmath)  

[Collection](#collection)

[Available Tools](#tools)

[Getting Started](#started)

Note: The current version of the data is V1.3. All the older versions can be found in "Old versions" with "Changes" file showing what has changed. The only change made from the current version (V1.3) compared to (V1.2) is annotating formulas correctly in Post and Comment XML files. By annotation, we mean putting formulas correctly in "math-container" HTML span tags with formula id.

# ARQMath lab at CLEF
[ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/) lab at [CLEF 2020](https://clef2020.clef-initiative.eu/).  focuses on mathematical information retrieval. There will be two tasks for this lab:
  ### Task 1 
  Given a math question (a question related to some mathematical information need that contains at least one formula), participants will retrieve a list of possible answers to that question, ranked based on relevance.
  
  ### Task 2
  Given a formula as a query, participants should retrieve formulas related to the formula query.
  
  ### Task 3
  This task is introduced in ARQMath-3, similar to Task 1, where the participants can return any answer (not necessarly from the previous MathStackExchange posts) to questions in task 1.
 
The data available for participants covers posts from the year 2010 to 2018. The topics for both tasks are selected from posts (questions) posted in 2019 for ARQMath-1, 2020 for ARQMath-2, and 2021 for ARQMath-3. Further information please check the ARQMath [webpage](https://www.cs.rit.edu/~dprl/ARQMath/). You may also consider joining the discussion forum [here](https://groups.google.com/forum/#!forum/arqmath-lab).
 
# Collection
In this lab, we will be using data from [Math Stack Exchange](https://math.stackexchange.com/) (MSE)The dateset for this lab is currently available on [Google Drive](https://drive.google.com/drive/folders/1ZPKIWDnhMGRaPNVLi1reQxZWTfH2R4u3?usp=sharing). This data was provided by [Archive](https://archive.org/) and several preprocessing have been done on the initial data. There are 7 files in this dataset:
  #### Users
  Users can post questions and answers and therefore each post is written by a user. Each user has a unique id along with other information such as display name, age, location, the date they created their profile and the reputations points earned based on their activities on MSE such as receiving an "up" vote on an answer given.
  #### Badges
  Besides the reputation for each user, they can have a list of badges they received. There are three classes of badges 3:bronze, 2:silver, and 1:gold. Each badge is linked to a user by user id.
  #### Votes
  Members of MSE, can give different votes to questions and answers. In the vote file, for each vote, there is a unique id, related post id, vote type [1 to 13], vote date and the user id of the voter.
  #### Tags  
  Each question on the MSE, can have different tags that are determined by the user posting the question. In tag file, one can find a list of all possible tags with their repetition count. However, in the post file, you can get the exact question tags.
 #### Comments
 Users can comment on both questions and answers. In the comment file, each comment has its own unique id, along with the related post id, the id of the user who wrote the comment, its creation date, its text, and score.
  #### PostLinks
  Each question on MSE can be associated with other questions; it can be related to another question or it can be its duplicate.
  In the post links file, each link has a unique id, the post id of the question, the post id of the related question (relatedpostid), the link type [1:related, 3:duplicate].
  #### Posts
  This is the main file for the task, where there are both questions and answers. Each post has a unique id, post type [1: question, 2:answer], the creation date, body, score and view count. For each answer, there is parent id which shows the question id for which the answer was provided. Each question has a title, set of tags and answer count.
  
 Here is summary of the fields in each xml file from the readme file provided by Archive:
 - Files:
   - **badges**.xml
       - UserId, e.g.: "420"
       - Name, e.g.: "Teacher"
       - Date, e.g.: "2008-09-15T08:55:03.923"
   - **comments**.xml
       - Id
       - PostId
       - Score
       - Text, e.g.: "@Stu Thompson: Seems possible to me - why not try it?"
       - CreationDate, e.g.:"2008-09-06T08:07:10.730"
       - UserId
   - **posts**.xml
       - Id
       - PostTypeId
          - 1: Question
          - 2: Answer
       - ParentID (only present if PostTypeId is 2)
       - AcceptedAnswerId (only present if PostTypeId is 1)
       - CreationDate
       - Score
       - ViewCount
       - Body
       - OwnerUserId
       - LastEditorUserId
       - LastEditorDisplayName="Jeff Atwood"
       - LastEditDate="2009-03-05T22:28:34.823"
       - LastActivityDate="2009-03-11T12:51:01.480"
       - CommunityOwnedDate="2009-03-11T12:51:01.480"
       - ClosedDate="2009-03-11T12:51:01.480"
       - Title
       - Tags
       - AnswerCount
       - CommentCount
       - FavoriteCount
   - **postlinks**.xml
     - Id
     - CreationDate
     - PostId
     - RelatedPostId
     - PostLinkTypeId
       - 1: Linked
       - 3: Duplicate
   - **users**.xml
     - Id
     - Reputation
     - CreationDate
     - DisplayName
     - EmailHash
     - LastAccessDate
     - WebsiteUrl
     - Location
     - Age
     - AboutMe
     - Views
     - UpVotes
     - DownVotes
   - **votes**.xml
     - Id
     - PostId
     - VoteTypeId
        - ` 1`: AcceptedByOriginator
        - ` 2`: UpMod
        - ` 3`: DownMod
        - ` 4`: Offensive
        - ` 5`: Favorite - if VoteTypeId = 5 UserId will be populated
        - ` 6`: Close
        - ` 7`: Reopen
        - ` 8`: BountyStart
        - ` 9`: BountyClose
        - `10`: Deletion
        - `11`: Undeletion
        - `12`: Spam
        - `13`: InformModerator
     - CreationDate
     - UserId (only for VoteTypeId 5)
     - BountyAmount (only for VoteTypeId 9)
	

# Available tools
To facilitate the data loading, the lab organizer provided a python code to read all the data and iterate over it. The code is available on [github](https://github.com/ARQMath/ARQMath). Also with this code, participants can view each thread (question along with answers and other related information) as html file. 

# Getting Started
The ARQMath google drive, contains 4 directories. All the files have version and only the version that should be used for the task is kept in the directory and the older versions are kept in Old versions directory.

The collection directory contains all the data files (2010-2018) that will be used for both tasks one and two. Each of the two tasks has its own directory. Note that these directories will be used by participants to train their model, and also the retrieval results for both tasks are from these documents.

For task one, there are three sample topics provided for now in Task1 directory. The sample qrel and query files are created for these three topics. Also, a sample retrieval file is provided which is in standard trec format and evaluation can be done with trec eval tools.

For task two, the data will be available soon.

Finally, the formula directory provides all the formulas in the collection in 2 files. The formula_latex.tsv file is showing the Latex representation of formulas.  There are 5 columns in these files showing formula id, post id, thread id, type of post they appeared in which can be question, answer, comment or title and finally formula itself which is represented accordingly. The MathMl.zip file contains two tsv files in the same format of latex file which show opt(operator tree) and slt (symbol layout tree) representation of formulas.

Note that all formulas have a unique id. In the collection, formulas are located in "math-container" tags. Using our provided tools, by defining the post id and formula id, participants are able to extract the formula, however, all the formulas are available in the tsv file. Also, it should be mention, our definition of formula is any string between two dollars ($) signs. Therefore, our dataset might contain noise (for instance, the cases that in the post, dollar sign is used as currency more than one time).

Check the [ARQMath forum](https://groups.google.com/forum/#!forum/arqmath-lab) for any further information.
