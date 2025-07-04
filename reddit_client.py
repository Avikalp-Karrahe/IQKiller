"""
Reddit Client for fetching job-related posts during analysis
"""
import requests
import requests.auth
import random
import time
from typing import List, Dict, Any, Optional
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, JOB_SUBREDDITS

class RedditClient:
    """Client for fetching Reddit posts from job-related subreddits"""
    
    def __init__(self):
        self.client_id = REDDIT_CLIENT_ID
        self.client_secret = REDDIT_CLIENT_SECRET
        self.user_agent = REDDIT_USER_AGENT
        self.access_token = None
        self.token_expires = 0
    
    def get_access_token(self) -> Optional[str]:
        """Get Reddit API access token"""
        if self.access_token and time.time() < self.token_expires:
            return self.access_token
            
        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        data = {'grant_type': 'client_credentials'}
        headers = {'User-Agent': self.user_agent}
        
        try:
            response = requests.post('https://www.reddit.com/api/v1/access_token',
                                   auth=auth, data=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.token_expires = time.time() + token_data['expires_in'] - 60  # 1 min buffer
                return self.access_token
        except Exception as e:
            print(f"Failed to get Reddit token: {e}")
        
        return None
    
    def get_hot_posts(self, subreddit: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get hot posts from a subreddit"""
        token = self.get_access_token()
        if not token:
            return []
        
        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': self.user_agent
        }
        
        try:
            url = f'https://oauth.reddit.com/r/{subreddit}/hot'
            params = {'limit': limit}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                for post in data['data']['children']:
                    post_data = post['data']
                    posts.append({
                        'title': post_data['title'],
                        'score': post_data['score'],
                        'num_comments': post_data['num_comments'],
                        'url': f"https://reddit.com{post_data['permalink']}",
                        'subreddit': post_data['subreddit'],
                        'created_utc': post_data['created_utc']
                    })
                
                return posts
        except Exception as e:
            print(f"Failed to fetch posts from r/{subreddit}: {e}")
        
        return []
    
    def get_random_job_posts(self, num_posts: int = 3) -> List[Dict[str, Any]]:
        """Get random posts from job-related subreddits"""
        all_posts = []
        
        # Try to get posts from multiple subreddits
        for subreddit in random.sample(JOB_SUBREDDITS, min(3, len(JOB_SUBREDDITS))):
            posts = self.get_hot_posts(subreddit, limit=2)
            all_posts.extend(posts)
        
        # Return random selection
        if all_posts:
            return random.sample(all_posts, min(num_posts, len(all_posts)))
        
        # Fallback posts if Reddit API fails
        return [
            {
                'title': '💡 Pro tip: Research the company culture before your interview',
                'score': 156,
                'num_comments': 23,
                'url': '#',
                'subreddit': 'careerguidance',
                'created_utc': time.time()
            },
            {
                'title': '🎯 STAR method for behavioral questions - game changer!',
                'score': 289,
                'num_comments': 47,
                'url': '#',
                'subreddit': 'jobs',
                'created_utc': time.time()
            },
            {
                'title': '🔥 Always prepare 3 questions to ask the interviewer',
                'score': 198,
                'num_comments': 31,
                'url': '#',
                'subreddit': 'careeradvice',
                'created_utc': time.time()
            }
        ]
    
    def format_posts_for_display(self, posts: List[Dict[str, Any]]) -> str:
        """Format posts for HTML display"""
        if not posts:
            return "<p>Loading career insights...</p>"
        
        html = '<div class="reddit-posts">'
        
        for post in posts:
            # Format time ago
            time_ago = int(time.time() - post['created_utc'])
            if time_ago < 3600:
                time_str = f"{time_ago // 60}m ago"
            elif time_ago < 86400:
                time_str = f"{time_ago // 3600}h ago"
            else:
                time_str = f"{time_ago // 86400}d ago"
            
            html += f'''
                <div class="reddit-post">
                    <div class="post-header">
                        <span class="subreddit">r/{post['subreddit']}</span>
                        <span class="post-time">{time_str}</span>
                    </div>
                    <h4 class="post-title">{post['title']}</h4>
                    <div class="post-stats">
                        <span class="upvotes">↑ {post['score']}</span>
                        <span class="comments">💬 {post['num_comments']}</span>
                    </div>
                </div>
            '''
        
        html += '</div>'
        return html

    def get_top_posts_of_week(self, subreddit: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Get top posts of the week from a subreddit"""
        token = self.get_access_token()
        if not token:
            print(f"No token for r/{subreddit}")
            return []

        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': self.user_agent
        }

        try:
            url = f'https://oauth.reddit.com/r/{subreddit}/top'
            params = {'limit': limit, 't': 'week'}  # t=week for top of the week
            
            print(f"Fetching from: {url} with params: {params}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"Response status for r/{subreddit}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                if 'data' in data and 'children' in data['data'] and len(data['data']['children']) > 0:
                    for post in data['data']['children']:
                        post_data = post['data']
                        
                        # Get full post content including body text
                        full_content = post_data.get('selftext', '').strip()
                        if not full_content:
                            # If no selftext, create a preview from the title
                            full_content = "Link post - click 'View Full Post' to see the discussion and content."
                        elif len(full_content) > 400:  # Truncate very long posts
                            full_content = full_content[:400] + "..."
                        
                        posts.append({
                            'title': post_data['title'],
                            'content': full_content,
                            'score': post_data['score'],
                            'num_comments': post_data['num_comments'],
                            'url': f"https://reddit.com{post_data['permalink']}",
                            'subreddit': post_data['subreddit'],
                            'created_utc': post_data['created_utc'],
                            'author': post_data['author'],
                            'flair': post_data.get('link_flair_text', '') or ''
                        })
                    
                    print(f"Successfully fetched {len(posts)} posts from r/{subreddit}")
                    return posts
                else:
                    print(f"No posts found in response for r/{subreddit}")
            else:
                print(f"API error for r/{subreddit}: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"Exception fetching posts from r/{subreddit}: {e}")
        
        return []

    def get_job_posts_by_subreddit(self) -> Dict[str, Dict[str, Any]]:
        """Get one top post of the week from each job-related subreddit"""
        subreddit_posts = {}
        
        for subreddit in JOB_SUBREDDITS:
            posts = self.get_top_posts_of_week(subreddit, limit=1)
            if posts:
                subreddit_posts[subreddit] = posts[0]
                print(f"✅ Successfully got post from r/{subreddit}")
            else:
                print(f"❌ Failed to get posts from r/{subreddit} - API credentials invalid")
                # Return empty dict if Reddit API fails - no fallbacks
                subreddit_posts[subreddit] = None
        
        # Filter out None values
        subreddit_posts = {k: v for k, v in subreddit_posts.items() if v is not None}
        
        return subreddit_posts

    def get_single_subreddit_post(self, subreddit: str) -> Optional[Dict[str, Any]]:
        """Get a single fresh post from a specific subreddit"""
        posts = self.get_top_posts_of_week(subreddit, limit=3)  # Get 3 to have variety
        if posts:
            # Return a random post from the top 3 for variety
            import random
            return random.choice(posts)
        else:
            # If Reddit API fails, return None - no fallbacks
            print(f"❌ Failed to refresh post from r/{subreddit} - API credentials invalid")
            return None

    def format_subreddit_posts_for_display(self, subreddit_posts: Dict[str, Dict[str, Any]]) -> str:
        """Format subreddit posts for HTML display with individual refresh buttons"""
        if not subreddit_posts:
            return "<p>Loading career insights...</p>"

        html = '<div class="reddit-posts-enhanced">'
        
        for subreddit, post in subreddit_posts.items():
            # Format time ago
            time_ago = int(time.time() - post['created_utc'])
            if time_ago < 3600:
                time_str = f"{time_ago // 60}m ago"
            elif time_ago < 86400:
                time_str = f"{time_ago // 3600}h ago"
            else:
                time_str = f"{time_ago // 86400}d ago"
            
            # Format flair
            flair_html = f'<span class="post-flair">{post["flair"]}</span>' if post.get('flair') else ''
            
            html += f'''
                <div class="reddit-post-enhanced" data-subreddit="{subreddit}">
                    <div class="post-header-enhanced">
                        <div class="subreddit-info">
                            <span class="subreddit-name">r/{subreddit}</span>
                            {flair_html}
                        </div>
                        <div class="post-meta">
                            <span class="post-time">{time_str}</span>
                            <button class="refresh-post-btn" onclick="refreshPost('{subreddit}')" title="Get new post from this subreddit">
                                🔄
                            </button>
                        </div>
                    </div>
                    <h4 class="post-title-enhanced">
                        <a href="{post['url']}" target="_blank" rel="noopener">{post['title']}</a>
                    </h4>
                    <div class="post-content-enhanced">
                        {post['content']}
                    </div>
                    <div class="post-stats-enhanced">
                        <div class="stats-left">
                            <span class="upvotes">↑ {post['score']}</span>
                            <span class="comments">💬 {post['num_comments']}</span>
                            <span class="author">👤 u/{post['author']}</span>
                        </div>
                        <a href="{post['url']}" target="_blank" class="view-full-btn" rel="noopener">
                            View Full Post →
                        </a>
                    </div>
                </div>
            '''
        
        html += '''
            </div>
            <script>
                function refreshPost(subreddit) {
                    console.log('Refreshing post for r/' + subreddit);
                    // Map subreddit names to button IDs
                    const buttonMap = {
                        'jobs': 'refresh-jobs',
                        'careerguidance': 'refresh-careerguidance', 
                        'cscareerquestions': 'refresh-cscareerquestions',
                        'careeradvice': 'refresh-careeradvice',
                        'ITCareerQuestions': 'refresh-ITCareerQuestions'
                    };
                    
                    const buttonId = buttonMap[subreddit];
                    if (buttonId) {
                        // Find and click the hidden Gradio button
                        const refreshBtn = document.getElementById(buttonId);
                        if (refreshBtn) {
                            refreshBtn.click();
                        } else {
                            console.log('Button not found:', buttonId);
                        }
                    }
                }
            </script>
        '''
        
        return html

    def format_posts_as_widget_cards(self, subreddit_posts: Dict[str, Dict[str, Any]]) -> str:
        """Format subreddit posts as compact widget cards for top display"""
        if not subreddit_posts:
            return "<div class='reddit-widgets-loading' style='text-align: center; padding: 2rem; color: rgba(255,255,255,0.6);'>Reddit API credentials invalid - no posts available</div>"

        html = '<div class="reddit-widgets-container">'
        
        for subreddit, post in subreddit_posts.items():
            # Format time ago
            time_ago = int(time.time() - post['created_utc'])
            if time_ago < 3600:
                time_str = f"{time_ago // 60}m"
            elif time_ago < 86400:
                time_str = f"{time_ago // 3600}h"
            else:
                time_str = f"{time_ago // 86400}d"
            
            # Truncate content for widget view
            widget_content = post['content']
            if len(widget_content) > 120:
                widget_content = widget_content[:120] + "..."
            
            # Format source display - use actual source for articles, r/subreddit for Reddit posts
            source_display = post['subreddit'] if post['subreddit'].startswith(('jobs', 'career', 'cs', 'IT')) else post['subreddit']
            if not source_display.startswith('r/'):
                source_prefix = ""  # For articles from Forbes, Harvard, etc.
            else:
                source_prefix = "r/"
            
            html += f'''
                <div class="reddit-widget-card" data-subreddit="{subreddit}">
                    <div class="widget-header">
                        <span class="widget-subreddit">{source_prefix}{source_display}</span>
                        <div class="widget-actions">
                            <span class="widget-time">{time_str}</span>
                            <button class="widget-refresh-btn" onclick="refreshPost('{subreddit}')" title="Refresh">
                                🔄
                            </button>
                        </div>
                    </div>
                    <h5 class="widget-title">
                        <a href="{post['url']}" target="_blank" rel="noopener">{post['title']}</a>
                    </h5>
                    <p class="widget-content">{widget_content}</p>
                    <div class="widget-stats">
                        <span class="widget-score">↑ {post['score']}</span>
                        <span class="widget-comments">💬 {post['num_comments']}</span>
                        <a href="{post['url']}" target="_blank" class="widget-link" rel="noopener">Read →</a>
                    </div>
                </div>
            '''
        
        html += '''
            </div>
            <script>
                function refreshPost(subreddit) {
                    console.log('Refreshing widget for r/' + subreddit);
                    const buttonMap = {
                        'jobs': 'refresh-jobs',
                        'careerguidance': 'refresh-careerguidance', 
                        'cscareerquestions': 'refresh-cscareerquestions',
                        'careeradvice': 'refresh-careeradvice',
                        'ITCareerQuestions': 'refresh-ITCareerQuestions'
                    };
                    
                    const buttonId = buttonMap[subreddit];
                    if (buttonId) {
                        const refreshBtn = document.getElementById(buttonId);
                        if (refreshBtn) {
                            refreshBtn.click();
                        }
                    }
                }
            </script>
        '''
        
        return html

# Global Reddit client instance
reddit_client = RedditClient() 