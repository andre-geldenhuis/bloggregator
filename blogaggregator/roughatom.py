def roughatom():
    '''
    Goes through all users and finds their Atom feed addresses.
    It then populates their posts with the feed.  Currently veryt simple
    For testing only.
    '''
    
    from blogaggregator.database import db
    from blogaggregator.user.models import User
    from blogaggregator.user.models import Post
    import feedparser
    from blogaggregator.utils import summarise_post, clean_feed
    
    from time import mktime
    from datetime import datetime
    
    #get all user Atom feeds
    for user in User.query.all():
        print user.atomfeed
        feed = feedparser.parse(user.atomfeed)
        
        #check if it is a valid feed
        if feed.bozo != 0:
            print "bad feed"
        else:
            entries=feed.entries
            
            #check for the existance of the posts in the database
            for post in entries:
                matching_post = Post.query.filter_by(atomuuid = post.id)
                if matching_post.count() == 0:  #no matching posts
                    created_at = datetime.fromtimestamp(mktime(post.published_parsed))
                    updated_at = datetime.fromtimestamp(mktime(post.updated_parsed))
                    content = post.content[0].value
                    summary = summarise_post(content)
                    new_post = Post.create(content = clean_feed(content),
                        summary = summary,
                        user_id=user.id,
                        atomuuid=post.id,
                        link=post.link,
                        created_at = created_at)
                
                
            post0=entries[0]
            dt = datetime.fromtimestamp(mktime(post0.updated_parsed))
            
            content=post0.content
            c0=content[0]
            current_post=c0.value
    1/0
    
