using System;
using UnityEngine;

[RequireComponent(typeof(SpriteRenderer))]
public class ElfMageAnimator : MonoBehaviour
{
    public string animationName = "Idle Blinking";
    [Range(1, 60)] public float framesPerSecond = 30;
    public bool loop = true;
    private SpriteRenderer spriteRenderer;
    private Sprite[] frames = Array.Empty<Sprite>();
    private float elapsed;
    private string loadedAnimation;

    void Awake() { spriteRenderer = GetComponent<SpriteRenderer>(); }

    public void Play(string name)
    {
        animationName = name;
        loadedAnimation = name;
        elapsed = 0;
        frames = Resources.LoadAll<Sprite>("ElfMage/PNG Sequences/" + name);
        Array.Sort(frames, (a, b) => string.CompareOrdinal(a.name, b.name));
        if (frames.Length == 0)
            Debug.LogError("ElfMage: sequência não encontrada: " + name, this);
    }

    void Update()
    {
        if (loadedAnimation != animationName) Play(animationName);
        if (frames.Length == 0) return;
        int index = Mathf.FloorToInt(elapsed * framesPerSecond);
        index = loop ? index % frames.Length : Mathf.Min(index, frames.Length - 1);
        spriteRenderer.sprite = frames[index];
        elapsed += Time.deltaTime;
    }
}
