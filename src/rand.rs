
/// The single place where we generate random material
/// for our own use.  These functions never fail,
/// they panic on error.

use ring::rand::{SystemRandom, SecureRandom};
use ring::error::Unspecified;
use ring::digest;
use msgs::codec;

/// Insulate the system RNG against having its output directly
/// published.  This is intended to prevent an adversarily broken
/// RNG being able to (eg) exfil state information in its output.
///
/// It seems somewhat unlikely that the system RNG is broken like
/// this, but the TLS1.3 RFC recommends doing this.
///
/// We just hash the output of the underlying generator.
struct PublicRandom(SystemRandom);

fn sha256(buf: &mut [u8]) {
    let h = digest::digest(&digest::SHA256, buf);
    buf.copy_from_slice(h.as_ref());
}

impl SecureRandom for PublicRandom {
    fn fill(&self, bytes: &mut [u8]) -> Result<(), Unspecified> {
        let mut buf = [0u8; 32];

        for ch in bytes.chunks_mut(32) {
            self.0.fill(&mut buf)?;
            sha256(&mut buf);
            let l = ch.len();
            ch.copy_from_slice(&buf[..l]);
        }

        Ok(())
    }
}

/// Fill the whole slice with random material.
/// The random material will be published on the wire.
pub fn fill_public_random(bytes: &mut [u8]) {
    PublicRandom(SystemRandom::new())
        .fill(bytes)
        .unwrap();
}

/// Fill the whole slice with random material.
/// The random material will be kept private.
pub fn fill_private_random(bytes: &mut [u8]) {
    SystemRandom::new()
        .fill(bytes)
        .unwrap();
}

/// Return a uniformly random u32.
pub fn random_public_u32() -> u32 {
    let mut buf = [0u8; 4];
    fill_public_random(&mut buf);
    codec::decode_u32(&buf)
        .unwrap()
}
