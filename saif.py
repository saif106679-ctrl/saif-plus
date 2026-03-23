import telebot
from telebot import types

# التوكن الخاص بك (تذكر تغييره لاحقاً للأمان)
API_TOKEN = '8311362193:AAF0ahoskmhZQMW_eFEiBfXANgK_zHNlfGM'
bot = telebot.TeleBot(API_TOKEN)

# قائمة المنتجات التجريبية
products = {
    "1": {"name": "اشتراك YouTube Premium (شهر)", "price": "2.5 BD"},
    "2": {"name": "اشتراك Gemini Advanced (شهر)", "price": "7.0 BD"},
    "3": {"name": "اشتراك شاهد VIP (شهر)", "price": "3.0 BD"}
}

# رسالة الترحيب وقائمة المنتجات
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for p_id, p_info in products.items():
        button = types.InlineKeyboardButton(
            text=f"{p_info['name']} - {p_info['price']}", 
            callback_data=f"buy_{p_id}"
        )
        markup.add(button)
    
    bot.send_message(message.chat.id, "أهلاً بك في متجر سيف الرقمي 🛒\nاختر الاشتراك المطلوب:", reply_markup=markup)

# التعامل مع الضغط على الأزرار
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_buy(call):
    product_id = call.data.split('_')[1]
    product = products[product_id]
    
    # طلب تأكيد الشراء أو إرسال تفاصيل الدفع
    response_text = f"لقد اخترت: {product['name']}\nالسعر: {product['price']}\n\nلإتمام الطلب، يرجى تحويل المبلغ عبر BenefitPay وإرسال صورة التحويل هنا."
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, response_text)

# تشغيل البوت
print("البوت يعمل الآن...")
bot.infinity_polling()