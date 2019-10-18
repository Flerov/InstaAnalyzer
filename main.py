#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @author https://github.com/Flerov/
# @version 0.1
# @updated 04.10.2019

from InstagramAPI import InstagramAPI
import colors as set
import datetime
import sys
import os


def unixtodate(unixid):
    return datetime.datetime.fromtimestamp(int(unixid)).strftime('%Y-%m-%d %H:%M:%S')


# First
def usage():  # called in line 68
    if len(sys.argv) == 1:
        return False
    return True


# Second
def get_api():  # called in line 71
    _api = InstagramAPI(sys.argv[1], sys.argv[2])
    if not _api.login():
        sys.stdout.write("\033[0;31mLogin failed | [Response]: %s | [Json]: %s\033[0;0m\n"
                         % api.LastResponse, api.LastJson)
        print("[Log]: System exit @method 'get_api'")
        sys.exit(0)
    return _api


# Third
def handle_session():  # called in line 73
    sys.stdout.write("\033[0;34mSession handler running\033[0;0m\n")
    if check_session():
        with open('session.txt', 'r') as ses:
            lines = ses.readlines()
            if len(lines) > 0:
                sys.stdout.write("\033[0;34m---------------------\n")
                for i in range(len(lines)):
                    sys.stdout.write("[{}] {}\n".format(i, lines[i].strip('\n')))
                sys.stdout.write("---------------------\033[0;0m\n")
            else:
                return False
            int_toLoad = len(lines)
            while int_toLoad > len(lines)-1:
                int_toLoad = int(input('Session number to load: '))
            # USE THESE VALUES TO LOAD LAST SESSION ! CHANGE MAINFUNCTION
            data = lines[int_toLoad].split('.')
            if not load_data(data[0], data[1], int(data[2]), data[3]):  # args : username:str, pk:str, mediaid:int, maxid:str
                sys.stdout.write("\033[0;31mFailed to load session\n\033[0;0m")
                print("[Log]: System exit @method 'handle_session'")
                sys.exit(0)
    else:
        # create Session save:
        sys.stdout.write("\033[0;34m* session.txt created\033[0;0m\n")
        return False


def check_session():
    path = os.getcwd()
    files = os.listdir(path)
    filename = 'session.txt'
    if filename in files:
        return True
    else:
        open(filename, 'w+')
        return False


def add_session(uname, pk, mediaid, maxid):
    path = os.getcwd()
    filename = 'session.txt'
    with open(filename, 'a') as ses:
        string = '{}.{}.{}.{}\n'.format(uname, pk, mediaid, maxid)
        ses.write(string)


# Fourth
def load_data(uname, pk, mediaid: int, maxid):  # called in line 53 # mediaid = id in list feed['items'] (ex. 0,1,2,..)
    api.getUserFeed(pk, maxid)
    feed = api.LastJson
    if 'fail' in feed['status']:
        return False
    handle_post_options(feed['items'][mediaid])  # args : post


def handle_post_options(post):  # called in line 68
    while True:
        sys.stdout.write("\n\n\033[0;34m------------------------\n"
                         "Post options:\n"
                         "     1. Post information (Now only for single pictures!)\n"
                         "     2. Filter comments\033[0;0m\n")
        choice = int(input(" > "))
        if choice == 1:
            handle_post_information(post)  # args : post type (single pic, carousel, video)
        elif choice == 2:
            handle_post_comments(post)


def handle_post_information(post):
    sys.stdout.write("\n\n\033[0;34m------------------------\n"
                     "Post information:\n"
                     "     Taken at:             [{0}]\n"
                     "     Post of you:          [{1}]\n"
                     "     Comment count:        [{2}]\n"
                     "     Like count:           [{3}]\n"
                     "     Liked by you:         [{4}]\n"
                     "     Can like comment:     [{5}]\n"
                     "     Is user private:      [{6}]\n"
                     "     Is user verified:     [{7}]\n"
                     "     Can viewer share:     [{8}]\n"
                     "     Can viewer save:      [{9}]\033[0;0m\n".format(unixtodate(post['taken_at']),
                                                                          post['photo_of_you'],
                                                                          post['comment_count'],
                                                                          post['like_count'],
                                                                          post['has_liked'],
                                                                          post['comment_likes_enabled'],
                                                                          post['user']['is_private'],
                                                                          post['user']['is_verified'],
                                                                          post['can_viewer_reshare'],
                                                                          post['can_viewer_save']))
    input(str('Press Enter to continue'))
    return True


def handle_post_comments(post):
    # first load comments, then analyze comments
    username, mediacomments = load_post_comments(post)
    if not username or not mediacomments:
        return
    analyze_post_comments(username, mediacomments)


def load_post_comments(post):
    try:
        sys.stdout.write("\033[0;34mFound [\033[0;32m{}\033[0;34m] comments on post\n\n".format(post['comment_count']))
        x = int(input("How many comments to load: "))
        username = post['user']['username']
        mediacomments = []
        mediaid = post['id']
        maxid = ''

        while len(mediacomments) < x:
            api.getMediaComments(mediaid, maxid)
            comments = api.LastJson
            for i in comments['comments']:
                mediacomments.append(i)
                if (len(mediacomments) % 100) == 0:
                    sys.stdout.write(
                        "Fetched [\033[0;32m{}/{}\033[0;34m] comments\n".format(len(mediacomments), x))
                if len(mediacomments) == x:
                    break
            if 'next_max_id' in comments:
                maxid = comments['next_max_id']
                continue
            else:
                sys.stdout.write("\n\033[0;0m(+)\033[0;31m Not able to load more comments! "
                                 "\033[0;0m->\033[0;34m Loaded: \033[0;32m[{}]\033[0;34m comments\n".
                                 format(len(mediacomments)))
                break

        sys.stdout.write("\n------------------------\n"
                         "Successfully loaded [{}] posts"
                         "\n------------------------\n\n".format(len(mediacomments)))
        return username, mediacomments
    except KeyboardInterrupt:
        return False


def analyze_post_comments(username, mediacomments):
    try:
        while True:
            expression = str(input(sys.stdout.write("\033[0;34mExpression: ")))
            filename = username + '_' + expression + '.txt'
            filteredcomments = []
            for i in mediacomments:
                if expression in i['text']:
                    filteredcomments.append(i)

            sys.stdout.write("Found [\033[0;32m{}\033[0;34m] matching comments\n".format(len(filteredcomments)))

            if not len(filteredcomments) == 0:
                if 'comments' not in os.listdir(os.getcwd()):
                    os.mkdir('comments')
                with open('comments/' + filename, 'w+') as file:
                    for i in filteredcomments:
                        string = '[TEXT : {}] [USERNAME : {}] [COMMENT CREATED : {}] [PK : {}] ' \
                                 '[USER PK : {}] [PRIVATE : {}] [PB URL : {}]\n' \
                                 '------------------------------------------------\n'. \
                            format(i['text'], i['user']['username'], unixtodate(i['created_at']), i['pk'],
                                   i['user']['pk'], i['user']['is_private'], i['user']['profile_pic_url'])
                        file.write(string)

                sys.stdout.write("\033[0;32mFurther information added to {}\033[0;0m\n".format(filename))
                input("\nPress Enter to continue!\033[0;34m ")
                sys.stdout.write("\n")
            else:
                sys.stdout.write("\033[0;31mNo file created!\033[0;0m\n")
    except KeyboardInterrupt:
        print("\nReturning!\n")
        return


def create_session(uname: str):
    check_session()


def get_post():
    sys.stdout.write("\033[0;34mUsername: \033[0;0m\n")
    uname = str(input("> "))
    api.searchUsername(uname)
    if 'fail' in api.LastJson['status']:
        sys.stdout.write("\033[0;31mInstagram has no user matching your input: %s\033[0;0m\n" % uname)
        return False
    create_session(uname)  # func to be implemented
    pk = api.LastJson['user']['pk']
    maxid = ''
    while True:
        api.getUserFeed(pk, maxid)
        feed = api.LastJson
        if 'fail' in feed['status']:
            return False
        for i in range(0, len(feed['items']) - 1):
            mediadata = feed['items'][i]
            sys.stdout.write("\033[0;34m"
                             "\n------------------------\n"
                             "Media number:  [\033[0;32m{0}\033[0;34m]\n"
                             "Like count:    [\033[0;32m{1}\033[0;34m]\n"
                             "Comment count: [\033[0;32m{2}\033[0;34m]\n"
                             .format(i,
                                     mediadata['like_count'],
                                     mediadata['comment_count']))
            if feed['items'][i]['caption'] is None:
                sys.stdout.write("Caption:       ["
                                 "\033[0;31m"
                                 "No Caption available"
                                 "\033[0;34m"
                                 "]\n")
            else:
                caption = mediadata['caption']['text']
                if len(caption) > 30:
                    caption = caption[:30] + ' (...)'
                sys.stdout.write("Caption:       [\033[0;32m{}\033[0;34m]\n".format(caption))

            if mediadata['media_type'] == 1:
                mediatype = 'Single Picture'
            elif mediadata['media_type'] == 2:
                mediatype = 'Video'
            elif mediadata['media_type'] == 8:
                xpics = len(mediadata['carousel_media'])
                mediatype = str(xpics) + ' Posts'

            sys.stdout.write("Media type:    [\033[0;32m{}\033[0;34m]"
                             "\n------------------------\n".format(mediatype))

        if feed['more_available']:
            sys.stdout.write("\033[0;34m\n"
                             "Load more Posts ? ([INPUT] = \033[0;31mNo\033[0;34m / "
                             "[ENTER] = \033[0;32mYes\033[0;34m)\033[0;0m\n")

        if not input("[Load more]: "):
            maxid = feed['next_max_id']
            continue
        sys.stdout.write("\n\033[0;34mChoose post by its media number\033[0;0m\n")
        mediaid = int(input("[Media number]: "))
        post = feed['items'][mediaid]
        add_session(uname, pk, mediaid, maxid)  # add session
        sys.stdout.write("\033[0;34mSession for current post created!\033[0;0m\n")
        handle_post_options(post)


def main():
    if not usage():
        print("\nUsage: python main.py <username> <password>\n")
        sys.exit(0)
    try:
        sys.stdout.write("\033[0;34mLoad a session?[Yes/No]\033[0;0m\n")
        input = str(input("> "))
        if 'y' in input.lower():
            session = handle_session()
        while True:
            get_post()
    #except Exception as e:
    #    sys.stdout.write("\n\n\033[0;0mInterruption detected\nCaused by: " + str(e.args))
    except KeyboardInterrupt:
        sys.stdout.write("\n\033[0;31mKeyboard Interrupt! \033[0;0m")
    finally:
        sys.stdout.write("\033[0;31mLogout!\n\033[0;0m")
        api.logout()


if __name__ == '__main__':
    api = get_api()
    main()

