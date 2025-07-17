from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_mail import Mail
from markupsafe import Markup

import requests
import markdown

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
        if not email:
            return jsonify({'message': 'Email is required'}), 400

        # POST to Strapi
        response = requests.post(f'{STRAPI_API}/subscribers', json={
            'data': {
                'email': email
            }
        })

        if response.status_code == 200 or response.status_code == 201:
            return jsonify({'message': 'Thank you for subscribing!'}), 200
        elif response.status_code == 400:
            error = response.json()
            if any("already taken" in msg.get('message', '') for err in error.get('error', {}).get('details', {}).get('errors', []) for msg in err.get('messages', [])):
                return jsonify({'message': "You're already subscribed!"}), 200
            return jsonify({'message': 'Subscription failed. Please try again.'}), 400
        else:
            return jsonify({'message': 'Something went wrong. Please try again.'}), 500

    except Exception as e:
        return jsonify({'message': f'Subscription failed: {e}'}), 500
        
@app.route('/blog')
@app.route('/category/<category_slug>')
def blog(category_slug=None):
    try:
        category_filter = f"&filters[categories][slug][$eq]={category_slug}" if category_slug else ""
        response = requests.get(
            f"{STRAPI_API}/blog-posts?populate=*&sort[0]=publishedAt:desc&pagination[limit]=9"
        )
        response.raise_for_status()
        print(response.text)
        result = response.json()

        posts = []
        for item in result.get('data', []):
            posts.append({
                'title': item.get('Title'),
                'slug': item.get('slug'),
                'thumbnail': STRAPI_URL + item.get('thumbnail', {}).get('formats', {}).get('small', {}).get('url', ''),
                'publishedDate': item.get('publishedDate')
            })

        return render_template('/blog/index.html', posts=posts, category_slug=category_slug)

    except Exception as e:
        return render_template('error.html', message=f"Error loading posts: {e}")


@app.route('/blog/<slug>')
def blog_detail(slug):

    try:
        # Get the selected blog post
        response = requests.get(f"{STRAPI_API}/blog-posts?filters[slug][$eq]={slug}&populate=*")
        data = response.json()['data']
        if not data:
            return render_template('error.html', message=f"Blog post not found for slug: {slug}")

        post_data = data[0]

        print("Strapi response:", response.json())

        post = {
            'title': post_data['Title'],
            'content': Markup(markdown.markdown(post_data['content'])),
            'slug': post_data['slug'],
            'thumbnail': STRAPI_URL + post_data.get('thumbnail', {}).get('formats', {}).get('medium', {}).get('url', ''),
            'publishedDate': post_data['publishedDate']
        }

        # Get recent posts
        recent_resp = requests.get(f"{STRAPI_API}/blog-posts?sort=publishedDate:desc&pagination[limit]=3&populate=thumbnail")
        recent = [
            {
                'title': item['Title'],
                'slug': item['slug'],
                'thumbnail': STRAPI_URL + item.get('thumbnail', {}).get('formats', {}).get('thumbnail', {}).get('url', ''),
                'publishedDate': post_data['publishedDate']
            }
            for item in recent_resp.json().get('data', [])
            if item['slug'] != slug  # Exclude current post
        ]

        # Get categories with post counts
        try:
            categories_resp = requests.get(f"{STRAPI_API}/categories?populate=blog_posts")
            categories_resp.raise_for_status()  # raises an exception if status is 4xx/5xx
            print("Strapi category response:", categories_resp.json())

            categories_json = categories_resp.json()
            categories = []

            if categories_json and 'data' in categories_json:
                for cat in categories_json['data']:
                    attributes = cat.get('attributes', {})
                    blog_posts = attributes.get('blog_posts', {}).get('data', [])
                    categories.append({
                        'name': attributes.get('name'),
                        'slug': attributes.get('slug'),
                        'count': len(blog_posts)
                    })
            else:
                print("No 'data' found in categories response")

            return render_template('/blog/blog_detail.html', post=post, recent=recent, categories=categories)

        except requests.exceptions.RequestException as req_err:
            return render_template('error.html', message=f"Request error while loading categories: {req_err}")
    except Exception as e:
        return render_template('error.html', message=f"Error loading blog: {e}")

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
