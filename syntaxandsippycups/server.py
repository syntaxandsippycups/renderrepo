from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_mail import Mail
from markupsafe import Markup

import requests
import markdown
import traceback

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

# Mailtrap configuration for testing
app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525  # You can also use 2525 or 25
app.config['MAIL_USERNAME'] = '2b74c9db1ccf2b'
app.config['MAIL_PASSWORD'] = '28058a12059d57'  # Replace with your actual password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

STRAPI_API = 'https://api.syntaxandsippycups.com/api'
STRAPI_URL = 'https://api.syntaxandsippycups.com'  # <-- add this

mail = Mail(app)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        email = request.json.get('email')
        print("Email received from front-end:", email)

        if not email:
            return jsonify({'message': 'Email is required'}), 400

        response = requests.post(f'{STRAPI_API}/subscribers', json={
            'data': {
                'email': email
            }
        })

        print('Strapi Response:', response.status_code, response.text)

        if response.status_code in [200, 201]:
            return jsonify({'message': 'Thank you for subscribing!'}), 200
        elif response.status_code == 400:
            return jsonify({'message': 'You have already be subscribed.'}), 200
        else:
            return jsonify({'message': 'Something went wrong. Please try again.'}), 500

    except Exception as e:
        print('Error during subscription:', str(e))
        return jsonify({'message': f'Subscription failed: {e}'}), 500


@app.route('/unsubscribe/<int:subscriber_id>', methods=['GET'])
def unsubscribe(subscriber_id):
    # Hit Strapi DELETE or unpublish endpoint
    try:
        # You can either delete or mark as unsubscribed (if you add a boolean field)
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
            f"{STRAPI_API}/blog-posts?populate=thumbnail,categories&sort[0]=publishedAt:desc&pagination[limit]=9{category_filter}"
        )
        response.raise_for_status()
        result = response.json()

        posts = []
        for item in result.get('data', []):
            attr = item.get('attributes', {})
            thumbnail_data = attr.get('thumbnail', {}).get('data')
            thumbnail_url = ''
            if thumbnail_data:
                thumbnail_attrs = thumbnail_data.get('attributes', {})
                formats = thumbnail_attrs.get('formats', {})
                thumbnail_url = (
                    formats.get('medium', {}).get('url') or
                    formats.get('small', {}).get('url') or
                    thumbnail_attrs.get('url', '')
                )

            posts.append({
                'title': attr.get('Title'),
                'slug': attr.get('slug'),
                'thumbnail': thumbnail_url,
                'publishedDate': attr.get('publishedDate')
            })


        return render_template('blog/index.html', posts=posts, category_slug=category_slug)

    except Exception as e:
        traceback.print_exc()
        return render_template('error/500.html', message=f"Error loading posts: {e}")




@app.route('/blog/<slug>')
def blog_detail(slug):
    try:
        resp = requests.get(f"{STRAPI_API}/blog-posts?filters[slug][$eq]={slug}&populate=*")
        resp.raise_for_status()
        data = resp.json().get('data', [])

        if not data:
            return render_template('error/500.html', message=f"No blog post found for slug={slug}")

        post_data = data[0]

        content_md = post_data.get('content', '')
        content_html = Markup(markdown.markdown(content_md))

        # Handle thumbnail URL
        thumbnail_data = post_data.get('thumbnail', {}).get('data')
        thumbnail_url = ''
        if thumbnail_data:
            # Depending on your exact structure:
            if 'attributes' in thumbnail_data:
                # fallback if sometimes there's attributes inside thumbnail data
                t_attrs = thumbnail_data['attributes']
                formats = t_attrs.get('formats', {})
                thumbnail_url = (
                    formats.get('medium', {}).get('url') or
                    formats.get('small', {}).get('url') or
                    t_attrs.get('url', '')
                )
            else:
                # if no attributes, URLs directly inside thumbnail_data
                formats = thumbnail_data.get('formats', {})
                thumbnail_url = (
                    formats.get('medium', {}).get('url') or
                    formats.get('small', {}).get('url') or
                    thumbnail_data.get('url', '')
                )

            if thumbnail_url.startswith('/'):
                thumbnail_url = BASE_URL + thumbnail_url

        post = {
            'title': post_data.get('Title', ''),
            'content': content_html,
            'slug': post_data.get('slug', ''),
            'thumbnail': thumbnail_url,
            'publishedDate': post_data.get('publishedDate', '')
        }

        # Fetch recent posts - adapt same logic as above
        recent_posts = []
        r = requests.get(f"{STRAPI_API}/blog-posts?sort[0]=publishedAt:desc&pagination[limit]=4&populate=thumbnail")
        r.raise_for_status()
        for item in r.json().get('data', []):
            # For recent posts also no attributes
            p = item
            s2 = p.get('slug')
            if s2 == slug:
                continue
            t2 = p.get('Title', '')
            date2 = p.get('publishedDate', '')
            thumb2 = ''
            td = p.get('thumbnail', {}).get('data')
            if td:
                if 'attributes' in td:
                    ta = td['attributes']
                    fm = ta.get('formats', {})
                    thumb2 = fm.get('thumbnail', {}).get('url') or ta.get('url', '')
                else:
                    fm = td.get('formats', {})
                    thumb2 = fm.get('thumbnail', {}).get('url') or td.get('url', '')
                if thumb2.startswith('/'):
                    thumb2 = BASE_URL + thumb2
            recent_posts.append({
                'title': t2,
                'slug': s2,
                'thumbnail': thumb2,
                'publishedDate': date2
            })

        # Fetch categories (adjust if categories data structure also no attributes)
        categories = []
        c = requests.get(f"{STRAPI_API}/categories?populate=blog_posts")
        c.raise_for_status()
        for cat in c.json().get('data', []):
            # If categories also no attributes:
            categories.append({
                'name': cat.get('name', ''),
                'slug': cat.get('slug', ''),
                'count': len(cat.get('blog_posts', {}).get('data', []))
            })

        return render_template('blog/blog_detail.html', post=post, recent=recent_posts, categories=categories)

    except Exception as e:
        traceback.print_exc()
        return render_template('error/500.html', message=f"Error in blog_detail: {e}")
@app.route('/clothing')
def clothing():
  return render_template('/clothing/index.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        #name = request.form['name']
        #email = request.form['email']
        #message = request.form['message']
        #subject = request.form['subject']

        name = form.name.data
        email = form.email.data
        message = form.message.data
        subject = form.subject.data

        # Validate form data
        if not name or not email or not message or not subject:
            flash('All fields are required!')
            return redirect(url_for('contact'))

        # Compose email
        msg = Message(subject='Contact Form Submission',
                      sender=email,
                      recipients=['wonderfullycreatedbooks@gmail.com'],
                      body=f"Name: {name}\nEmail: {email}\nSubject: {subject}\nMessage: {message}")

        # Send email
        mail.send(msg)
        flash('Thank you for your message!')
        return redirect(url_for('contact'))
    return render_template('/contact/index.html')

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
