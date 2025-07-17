import { sendNewPostEmail } from '../../../../utils/email';

export default {
  async afterCreate({ result }) {
    try {
      const fullPost = await strapi.entityService.findOne('api::blog-post.blog-post', result.id, {
        populate: ['thumbnail'],
      });

      const title = fullPost.Title; // Match your content type exactly
      const content = fullPost.content || '';
      const slug = fullPost.slug;
      const thumbnailUrl = fullPost.thumbnail?.url
        ? `https://api.syntaxandsippycups.com${fullPost.thumbnail.url}`
        : null;

      const subscribers = await strapi.entityService.findMany('api::subscriber.subscriber' as any);

      if (Array.isArray(subscribers)) {
        for (const sub of subscribers) {
          if (sub && typeof sub.email === 'string') {
            await sendNewPostEmail(
              sub.email,
              title,
              content,
              slug,
              sub.id // pass subscriberId
            );
          }
        }
      }
    } catch (err) {
      strapi.log.error('Error sending blog post emails', err);
    }
  },
};
