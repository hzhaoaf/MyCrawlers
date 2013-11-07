#coding=utf8
import urllib2, random
import os, time

user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0', \
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0', \
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ \
        (KHTML, like Gecko) Element Browser 5.0', \
        'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)', \
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)', \
        'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14', \
        'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) \
        Version/6.0 Mobile/10A5355d Safari/8536.25', \
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/28.0.1468.0 Safari/537.36', \
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']

def search(queryStr):
    queryStr = urllib2.quote(queryStr)

    proxy_handler = urllib2.ProxyHandler({"http":'127.0.0.1:8087', "https":'127.0.0.1:8087'})
    opener = urllib2.build_opener(proxy_handler)
    #opener.addheaders = [('User-agent', user_agents[index])]
    urllib2.install_opener(opener)
    #urllib2.urlopen('http://blog.chinaunix.net/uid-23500957-id-3794837.html')

    url = 'https://www.google.com.hk/search?hl=en&q=%s&num=100' % queryStr
    print 'url is ', url
    request = urllib2.Request(url)
    index = random.randint(0, 9)
    user_agent = user_agents[index]
    request.add_header('User-agent', user_agent)
    response = urllib2.urlopen(request)
    html = response.read()
    return html

save_dir = 'htmls'
if not os.path.isdir(save_dir):
    os.mkdir(save_dir)


def save_list(filename, rlist):
    fw = open(filename, 'w+')
    fw.write('\n'.join(rlist))
    fw.close()

def search_by_person():
    '''
    根据query里的30个文件，每个文件每行query进行搜索，搜索一个后停止5s
    '''
    query_dir = 'query'
    files = os.listdir(query_dir)
    retry = 0
    total = 0
    for f in files:
        try:
            parts = f.split('.')
            if not os.path.isdir('%s/%s' % (save_dir, parts[0])):
                os.mkdir('%s/%s' % (save_dir, parts[0]))
            lines = open('%s/%s' % (query_dir, f), 'r').readlines()
            for i, query in enumerate(lines):

                successed_queries = open('successed_queries.txt', 'r').readlines()
                successed_queries = [l.strip() for l in successed_queries]
                query = query.strip()
                wfilename = '%s/%s/%s_%s.html' % (save_dir, parts[0], str(i+1), query[:2])
                try:
                    if wfilename in successed_queries:
                        print '%s has been crawled!' % wfilename
                        continue
                    if not query:
                        continue
                    start = time.time()
                    print 'search person %s, No.%s query %s' % (parts[0], i+1, query)
                    html = search(query)
                    #import pdb;pdb.set_trace()
                    fw = open(wfilename, 'w+')
                    fw.write(html)
                    fw.close()
                    successed_queries.append(wfilename)
                    save_list('successed_queries.txt', successed_queries)
                    total += 1
                    print 'succesed, html file saved in %s, cost %.2fs, total %s\n' % (wfilename, time.time() - start, total)
                    retry = 0
                    time.sleep(30)
                except Exception as e:
                    print 'error occured: %s, personfile %s No.%s query is %s\n' % (e, f, i+1, query)
                    error_queries = open('error_queries.txt', 'r').readlines()
                    error_queries = set([l.strip() for l in error_queries])
                    error_queries.add(wfilename)
                    save_list('error_queries.txt', list(error_queries))
                    time.sleep(3600 * 2)
                    retry += 1
                    if retry > 3:
                        print 'retry times more than 3, quit this query person\n'
                        break
                    else:
                        print 'retry times less than 3, sleep 3 seconds and continue\n'
                        continue
        except Exception as e:
            print 'error occured: %s, in file %s' % (e, f)
            time.sleep(10)
            continue

def crawl_error_list():
    lines = open('error_error_queries.txt')
    total = 0
    for cnt, l in enumerate(lines):
        successed_queries = open('error_error_successed_queries.txt', 'r+').readlines()
        successed_queries = [q.strip() for q in successed_queries]
        wfilename = l.strip()
        try:
            if wfilename in successed_queries:
                print '%s has been crawled!' % wfilename
                continue
            parts = wfilename.split('/')
            query_num = parts[1]
            index = int(parts[2].split('_')[0])
            query_lines = open('query/%s.txt' % query_num, 'r').readlines()
            error_query = query_lines[index-1]
            start = time.time()
            print 'search %s error query %s' % (cnt+1, wfilename)
            html = search(error_query)
            #import pdb;pdb.set_trace()
            fw = open(wfilename, 'w+')
            fw.write(html)
            fw.close()
            successed_queries.append(wfilename)
            save_list('error_successed_queries.txt', successed_queries)
            total += 1
            print 'succesed, html file saved in %s, cost %.2fs, total %s\n' % (wfilename, time.time() - start, total)
            time.sleep(30)
        except Exception as e:
            print 'error occured: %s, %s\n' % (e, l.strip())
            error_queries = open('error_error_queries2.txt', 'r').readlines()
            error_queries = set([l.strip() for l in error_queries])
            error_queries.add(wfilename)
            save_list('error_error_queries.txt', list(error_queries))
            time.sleep(3600 * 2)


if __name__ == '__main__':
    #html = search('china USA')
    #fw = open('test_google.com', 'w+')
    #fw.write(html)
    #fw.close()
    #search_by_person()
    crawl_error_list()
