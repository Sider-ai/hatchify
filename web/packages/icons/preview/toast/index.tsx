import type React from 'react'
import { createRef, forwardRef, type RefObject, useEffect, useImperativeHandle, useState } from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'

// 消息类型枚举
export enum MessageType {
  SUCCESS = 'success',
  ERROR = 'error',
  INFO = 'info',
  WARNING = 'warning',
}

// 单个Toast属性接口
interface ToastProps {
  message: string
  type: MessageType
  duration?: number
  onClose?: () => void
}

// Toast组件状态接口
interface ToastItem extends ToastProps {
  id: number
}

// Toast容器引用接口
export interface ToastContainerRef {
  show: (message: string, type?: MessageType, duration?: number) => number
  success: (message: string, duration?: number) => number
  error: (message: string, duration?: number) => number
  info: (message: string, duration?: number) => number
  warning: (message: string, duration?: number) => number
  close: (id: number) => void
}

// Toast服务接口
export interface ToastService {
  show: (message: string, type?: MessageType, duration?: number) => number | undefined
  success: (message: string, duration?: number) => number | undefined
  error: (message: string, duration?: number) => number | undefined
  info: (message: string, duration?: number) => number | undefined
  warning: (message: string, duration?: number) => number | undefined
  close: (id: number) => void
}

// 单个Toast组件
const Toast: React.FC<ToastProps> = ({ message, type, duration = 3000, onClose }) => {
  const [visible, setVisible] = useState<boolean>(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false)
      setTimeout(() => {
        onClose?.()
      }, 300) // 动画结束后移除
    }, duration)

    return () => clearTimeout(timer)
  }, [duration, onClose])

  return <div className={`toast toast-${type} ${visible ? 'show' : 'hide'}`}>{message}</div>
}

// ToastContainer组件管理多个Toast
const ToastContainer = forwardRef<ToastContainerRef, object>((_, ref) => {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  // 显示一条新消息
  const show = (message: string, type: MessageType = MessageType.INFO, duration: number = 3000): number => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, message, type, duration }])
    return id
  }

  // 移除指定消息
  const close = (id: number): void => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }

  // 各类消息的快捷方法
  const success = (message: string, duration?: number): number => show(message, MessageType.SUCCESS, duration)
  const error = (message: string, duration?: number): number => show(message, MessageType.ERROR, duration)
  const info = (message: string, duration?: number): number => show(message, MessageType.INFO, duration)
  const warning = (message: string, duration?: number): number => show(message, MessageType.WARNING, duration)

  // 暴露方法给外部使用
  useImperativeHandle(ref, () => ({
    show,
    success,
    error,
    info,
    warning,
    close,
  }))

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <Toast key={toast.id} message={toast.message} type={toast.type} duration={toast.duration} onClose={() => close(toast.id)} />
      ))}
    </div>
  )
})
ToastContainer.displayName = 'ToastContainer'

// 创建一个全局的Toast服务
export const toast: ToastService = (() => {
  let containerRef: RefObject<ToastContainerRef> | null = null

  // 确保DOM已加载
  if (typeof document !== 'undefined') {
    const div = document.createElement('div')
    div.id = 'toast-root'
    document.body.appendChild(div)

    const root = ReactDOM.createRoot(div)
    // @ts-expect-error
    containerRef = createRef<ToastContainerRef>()
    root.render(<ToastContainer ref={containerRef} />)
  }

  return {
    show: (message: string, type?: MessageType, duration?: number) => containerRef?.current?.show(message, type, duration),
    success: (message: string, duration?: number) => containerRef?.current?.success(message, duration),
    error: (message: string, duration?: number) => containerRef?.current?.error(message, duration),
    info: (message: string, duration?: number) => containerRef?.current?.info(message, duration),
    warning: (message: string, duration?: number) => containerRef?.current?.warning(message, duration),
    close: (id: number) => containerRef?.current?.close(id),
  }
})()

export default toast
