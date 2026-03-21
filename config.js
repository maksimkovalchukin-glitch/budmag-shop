const CONFIG = {
  // n8n webhooks — замінити на свої URL
  webhooks: {
    order: 'https://n8n.automaticly.org/webhook/shop-order',
    chat:  'https://n8n.automaticly.org/webhook/shop-chat',
  },
  shop: {
    name: 'Будівля.ua',
    phone: '+380 50 000 00 00',
    email: 'info@budivlya.ua',
    workHours: 'Пн-Пт 9:00–18:00',
  },
  dataPath: './data',
  itemsPerPage: 24,

  // Нова Пошта API — безкоштовний ключ на developers.novaposhta.ua
  novaPoshtaKey: '0f508b706ee58b95f8216c430b079a97',

  // Укрпошта API — безкоштовний ключ на dev.ukrposhta.ua
  ukrPoshtaKey: '',
};
