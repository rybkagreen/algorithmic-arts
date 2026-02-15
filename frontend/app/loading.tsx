'use client';

import { motion } from 'framer-motion';

export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="text-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="mx-auto size-12 border-4 border-primary border-t-transparent rounded-full mb-4"
        />
        <h2 className="text-xl font-semibold">Загрузка...</h2>
        <p className="text-muted-foreground mt-2">Подготовка данных для отображения</p>
      </div>
    </div>
  );
}