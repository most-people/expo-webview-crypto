const GunPeers = [
  'https://gun-manhattan.herokuapp.com/gun',
  'https://api.most.box/gun',
  'https://gun.most.red/gun',
]
const gun = window.Gun({
  peers: GunPeers,
})
window.user = gun.user()
window.user.login = async (username, password) => {
  window.user.leave()
  return new Promise((resolve) => {
    window.user.auth(username, password, (ack) => {
      if (ack.err) {
        resolve({ ok: false, message: '登录失败', data: ack.err })
        window.user.create(username, password, (ack) => {
          if (ack.err) {
            resolve({ ok: false, message: '注册失败', data: ack.err })
          } else {
            resolve({ ok: true, message: '注册成功' })
          }
        })
      } else {
        resolve({ ok: true, message: '登录成功' })
      }
    })
  })
}
