#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from InstagramAPI import InstagramAPI
import colors as set
import datetime
import sys


def unixtodate(unix):
    return datetime.datetime.fromtimestamp(int(unix)).strftime('%Y-%m-%d %H:%M:%S')


def searchcomments():
    try:
        set.color(set.BLUE)
        username = str(input("Username: "))
        api.searchUsername(username)

        if 'fail' in api.LastJson['status']:
            set.color(set.RED)
            print("Invalid username")
            return False

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
                                 "[ENTER] = \033[0;32mYes\033[0;34m)\n")

            if not input("[Load more]: "):
                maxid = feed['next_max_id']
                continue

            sys.stdout.write("\nChoose post to download by its media number\n")
            try:
                postnumber = int(input("[Media number]: "))
                post = feed['items'][postnumber]

                sys.stdout.write("\n\n------------------------\n"
                                 "Post options:\n"
                                 "     1. Post information\n"
                                 "     2. Filter comments\n")
                choice = int(input(" > "))

                if choice == 1:
                    sys.stdout.write("\n\n------------------------\n"
                                     "Post information:\n"
                                     "     Taken at:             [{0}]\n"
                                     "     Photo of you:         [{1}]\n"
                                     "     Comment count:        [{2}]\n"
                                     "     Like count:           [{3}]\n"
                                     "     Liked by you:         [{4}]\n"
                                     "     Can like comment:     [{5}]\n"
                                     "     Original height:      [{6}]\n"
                                     "     Original width:       [{7}]\n"
                                     "     Is user private:      [{8}]\n"
                                     "     Is user verified:     [{9}]\n"
                                     "     Can viewer share:     [{10}]\n"
                                     "     Top likers:           [{11}]\n"
                                     "     Can viewer save:      [{12}]\n".format(unixtodate(post['taken_at']),
                                                                                  post['photo_of_you'],
                                                                                  post['comment_count'],
                                                                                  post['like_count'],
                                                                                  post['has_liked'],
                                                                                  post['comment_likes_enabled'],
                                                                                  post['original_height'],
                                                                                  post['original_width'],
                                                                                  post['user']['is_private'],
                                                                                  post['user']['is_verified'],
                                                                                  post['can_viewer_reshare'],
                                                                                  post['top_likers'],
                                                                                  post['can_viewer_save']))

                    if post['media_type'] == 2:
                        sys.stdout.write("     View count:           [{0}]\n"
                                         "     Video duration:       [{1}]\n"
                                         "     Audio available:      [{2}]\n".format(post['view_count'],
                                                                                     post['video_duration'],
                                                                                     post['has_audio']))

                    input(str('Press Enter to continue'))

                elif choice == 2:
                    try:
                        sys.stdout.write("Found [\033[0;32m{}\033[0;34m] comments on post\n\n".format(post['comment_count']))
                        x = int(input("How many comments to load: "))
                        mediacomments = []
                        mediaid = post['id']
                        maxid = ''

                        while len(mediacomments) < x:
                            api.getMediaComments(mediaid, maxid)
                            comments = api.LastJson
                            with open('session/'+username+'.txt', 'w+') as ses:
                                for i in comments['comments']:
                                    mediacomments.append(i)
                                    ses.append(str(i)+'\n')
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

                        while True:
                            expression = str(input("Expression: "))
                            filename = username + '_' + expression + '.txt'
                            filteredcomments = []
                            for i in mediacomments:
                                if expression in i['text']:
                                    filteredcomments.append(i)

                            sys.stdout.write("Found [\033[0;32m{}\033[0;34m] matching comments\n".format(len(filteredcomments)))
                            sys.stdout.write("\033[0;32mAdding further information to {}\033[0;0m\n".format(filename))

                            if not len(filteredcomments) == 0:
                                with open('comments/'+filename, 'w+') as file:
                                    for i in filteredcomments:
                                        string = '[TEXT : {}] [USERNAME : {}] [COMMENT CREATED : {}] [PK : {}] ' \
                                                 '[USER PK : {}] [PRIVATE : {}] [PB URL : {}]\n' \
                                                 '------------------------------------------------\n'.\
                                            format(i['text'], i['user']['username'], unixtodate(i['created_at']), i['pk'],
                                                   i['user']['pk'], i['user']['is_private'], i['user']['profile_pic_url'])
                                        file.write(string)

                                input("\nPress Enter to continue!\033[0;34m ")
                                sys.stdout.write("\n")
                            else:
                                sys.stdout.write("\033[0;31mNo file created!\n")

                    except KeyboardInterrupt:
                        return

            except ValueError:
                sys.stdout.write("\n\n\033[0;31mError occured bad format!\033[0;0m\n")
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("-----------------------------------------------------\n"
              "Usage: python3 main.py 'your_username' 'your_password'\n"
              "-----------------------------------------------------\n")
        sys.exit(0)
    api = InstagramAPI(sys.argv[1], sys.argv[2])
    if not api.login():
        sys.exit(0)

    try:
        while True:
            searchcomments()
    except Exception:
        sys.stdout.write("\n\n\033[0;0mInterruption detected\n")
    finally:
        sys.stdout.write("\n\033[0;31mLogout!\n\033[0;0m")
        api.logout()
