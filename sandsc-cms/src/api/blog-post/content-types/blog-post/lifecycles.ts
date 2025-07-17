import { sendNewPostEmail } from '../../../../utils/email';

export default {
  async afterCreate(event) {
    try {
      const { result } = event;

      // Get full blog post with relations (thumbnail)
      const fullPost = await strapi.entityService.findOne(
        'api::blog-post.blog-post',
        result.id,
        {
          populate: ['thumbnail'],
        }
      );

      const title = fullPost.title;
      const content = fullPost.content || '';
      const slug = fullPost.slug;
      const thumbnailUrl = fullPost.thumbnail?.url
        ? `https://api.syntaxandsippycups.com${fullPost.thumbnail.url}`
        : null;

      const subscribers = await strapi.entityService.findMany('api::subscriber.subscriber' as any);

      for (const sub of subscribers) {
        if (sub && typeof sub.email === 'string') {
          await sendNewPostEmail(
            sub.email,
            title,
            content,
            slug,
            thumbnailUrl
            sub.id // pass subscriber ID
          );
        }
      }
    } catch (err) {
      strapi.log.error('Error sending blog post emails', err);
    }
  },
};
