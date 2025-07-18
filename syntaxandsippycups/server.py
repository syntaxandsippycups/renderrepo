from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_mail import Mail, Message
from markupsafe import Markup

import requests
import markdown
import traceback

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'


STRAPI_API = 'https://honorable-fruit-946f81aecf.strapiapp.com/api'
STRAPI_URL = 'https://honorable-fruit-946f81aecf.strapiapp.com'

mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        email = request.json.get('email')
        if not email:
            return jsonify({'message': 'Email is required'}), 400

        response = requests.post(f'{STRAPI_API}/subscribers', json={
            'data': {
                'email': email
            }
        })

        if response.status_code in [200, 201]:
            return jsonify({'message': 'Thank you for subscribing!'}), 200
        elif response.status_code == 400:
            return jsonify({'message': 'You have already be subscribed.'}), 200
        else:
            return jsonify({'message': 'Something went wrong. Please try again.'}), 500

    except Exception as e:
        return jsonify({'message': f'Subscription failed: {e}'}), 500

@app.route('/unsubscribe/<int:subscriber_id>', methods=['GET'])
def unsubscribe(subscriber_id):
    try:
        response = requests.delete(f"{STRAPI_API}/subscribers/{subscriber_id}")
        if response.status_code in (200, 204):
            return render_template("/unsubscribe/success.html")
        else:
            return render_template("/unsubscribe/failed.html", error=response.text)
    except Exception as e:
        return render_template("/unsubscribe/failed.html", error=str(e))

@app.route('/blog')
@app.route('/category/<category_slug>')
def blog(category_slug=None):
    try:
        category_filter = f"&filters[categories][slug][$eq]={category_slug}" if category_slug else ""
        response = requests.get(
            f"{STRAPI_API}/blog-posts?populate=*&sort[0]=publishedDate:desc&pagination[limit]=9{category_filter}"
        )
        response.raise_for_status()
        result = response.json()

        posts = []
        for item in result.get('data', []):
            thumbnail = item.get('thumbnail', {})
            formats = thumbnail.get('formats', {}) if thumbnail else {}
            thumbnail_url = (
                formats.get('medium', {}).get('url') or
                formats.get('small', {}).get('url') or
                thumbnail.get('url', '')
            )

            posts.append({
                'title': item.get('Title', ''),
                'slug': item.get('slug', ''),
                'thumbnail': thumbnail_url,
                'publishedDate': item.get('publishedDate', '')
            })

        return render_template('/blog/index.html', posts=posts, category_slug=category_slug)

    except Exception as e:
        traceback.print_exc()
        return render_template('/error/500.html', message=f"Error loading posts: {e}")

@app.route('/blog/<slug>')
def blog_detail(slug):
    try:
        # Fetch the blog post
        resp = requests.get(f"{STRAPI_API}/blog-posts?filters[slug][$eq]={slug}&populate=*")
        resp.raise_for_status()
        data = resp.json().get('data', [])
        if not data:
            return render_template('error/500.html', message=f"No blog post found for slug={slug}")

        post_data = data[0]

        # Process blog post content and thumbnail
        content_md = post_data.get('content', '')
        thumbnail_url = ''
        thumb_data = post_data.get('thumbnail')
        if thumb_data:
            formats = thumb_data.get('formats', {})
            thumbnail_url = (
                formats.get('medium', {}).get('url') or
                formats.get('small', {}).get('url') or
                thumb_data.get('url', '')
            )

        post = {
            'title': post_data.get('Title', ''),
            'content': Markup(markdown.markdown(content_md)),
            'slug': post_data.get('slug', ''),
            'thumbnail': thumbnail_url,
            'publishedDate': post_data.get('publishedDate', '')
        }

        # Fetch recent posts (excluding this one)
        recent_posts = []
        r = requests.get(f"{STRAPI_API}/blog-posts?sort[0]=publishedAt:desc&pagination[limit]=4&populate=thumbnail")
        r.raise_for_status()
        for item in r.json().get('data', []):
            if item.get('slug') == slug:
                continue
            td = item.get('thumbnail')
            formats = td.get('formats', {}) if td else {}
            thumb2 = formats.get('thumbnail', {}).get('url') or td.get('url', '') if td else ''
            recent_posts.append({
                'title': item.get('Title', ''),
                'slug': item.get('slug', ''),
                'thumbnail': thumb2,
                'publishedDate': item.get('publishedDate', '')
            })

        # 🛠️ FIX: Pull categories from the current post
        categories_raw = post_data.get('categories', [])

        categories = [
            {
                'id': cat['id'],
                'title': cat.get('Title', ''),
                'slug': cat.get('slug', ''),
                'count': len(cat.get('blog_posts', [])) if isinstance(cat.get('blog_posts'), list) else 0
            }
            for cat in categories_raw
        ]

        return render_template('blog/blog_detail.html', post=post, recent=recent_posts, categories=categories)

    except Exception as e:
        traceback.print_exc()
        return render_template('error/500.html', message=f"Error in blog_detail: {e}")


@app.route('/clothing')
def clothing():
    return render_template('/clothing/index.html')


@app.route('/digitalart')
def digitalart():
    return render_template('/digitalart/index.html')

@app.route('/digitalart/portraits')
def portraits():
    return render_template('/digitalart/portraits/index.html')

@app.route('/digitalart/portraits/minimal')
def minimal():
    return render_template('/digitalart/portraits/minimal/index.html')

@app.route('/digitalart/portraits/minimalbg')
def minimalbg():
    return render_template('/digitalart/portraits/minimalbg/index.html')

@app.route('/digitalart/prints')
def prints():
    return render_template('/digitalart/prints/index.html')

@app.route('/poetry')
def poetry():
    return render_template('/poetry/index.html')

@app.route('/about/ourstory')
def ourstory():
    return render_template('/about/ourstory/index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
