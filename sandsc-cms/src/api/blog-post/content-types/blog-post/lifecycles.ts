import { sendNewPostEmail } from '../../../../utils/email';

export default {
  async afterCreate({ result }) {
    try {
      const subscribers = await strapi.entityService.findMany('api::subscriber.subscriber' as any);

      for (const sub of subscribers as { email: string }[]) {
        if (sub.email) {
          await sendNewPostEmail(
            sub.email,
            result.title,
            result.content,   // Make sure "content" is a field in your blog post
            result.slug       // Make sure "slug" is a field in your blog post
          );
        }
      }
    } catch (err) {
      strapi.log.error('Error sending blog post emails', err);
    }
  },
};
